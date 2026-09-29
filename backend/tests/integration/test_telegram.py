"""OTP o'z Telegram botimiz orqali: ulash, kod yuborish, SMS'ga qaytish, xavfsizlik."""

import pytest
from pydantic import SecretStr

from app.application.common.interfaces import TelegramChatUnavailable
from app.domain.common.errors import ServiceUnavailableError
from tests.conftest import DeviceKey, login

PHONE = "+998901234567"
SECRET = "s" * 40
USER_ID = 111222333


class FakeBot:
    def __init__(self) -> None:
        self.sent: list[tuple[int, str, dict | None]] = []
        self.blocked: set[int] = set()
        self.down = False

    async def send_message(self, chat_id: int, text: str, reply_markup=None) -> None:
        if self.down:
            raise ServiceUnavailableError()
        if chat_id in self.blocked:
            raise TelegramChatUnavailable()
        self.sent.append((chat_id, text, reply_markup))


@pytest.fixture
def bot(container, settings):
    fake = FakeBot()
    container.telegram = fake
    settings.telegram_webhook_secret = SecretStr(SECRET)
    settings.telegram_bot_username = "finora_test_bot"
    return fake


def _msg(**fields):
    base = {"chat": {"id": USER_ID, "type": "private"},
            "from": {"id": USER_ID, "language_code": "uz"}}
    return {"update_id": 1, "message": {**base, **fields}}


async def _hook(client, update, secret=SECRET):
    return await client.post("/v1/telegram/webhook", json=update,
                             headers={"X-Telegram-Bot-Api-Secret-Token": secret})


async def _link(client, phone=PHONE, user_id=USER_ID):
    upd = _msg(contact={"phone_number": phone.lstrip("+"), "user_id": user_id})
    upd["message"]["from"]["id"] = user_id
    upd["message"]["chat"]["id"] = user_id
    assert (await _hook(client, upd)).status_code == 200


async def _request_otp(client, phone=PHONE, **extra):
    return await client.post("/v1/auth/otp", json={
        "phone": phone, "device_id": DeviceKey().installation_id, **extra})


async def test_start_offers_share_button(client, bot):
    r = await _hook(client, _msg(text="/start login"))
    assert r.status_code == 200
    chat_id, text, markup = bot.sent[-1]
    assert chat_id == USER_ID and "ulashing" in text
    assert markup["keyboard"][0][0]["request_contact"] is True


async def test_code_goes_to_telegram_after_linking_not_sms(client, container, bot):
    await _link(client)
    assert "shu chatga keladi" in bot.sent[-1][1]
    r = await _request_otp(client)
    assert r.status_code == 200
    assert r.json()["telegram_bot_url"] == "https://t.me/finora_test_bot?start=login"
    assert container.sms.outbox == []  # SMS yuborilmadi
    chat_id, text, _ = bot.sent[-1]
    code = text.split("kodi ")[1][:6]
    assert chat_id == USER_ID and code.isdigit()


async def test_login_with_telegram_code(client, container, bot):
    await _link(client)
    device = DeviceKey()
    await client.post("/v1/auth/otp", json={"phone": PHONE, "device_id": device.installation_id})
    code = bot.sent[-1][1].split("kodi ")[1][:6]
    r = await client.post("/v1/auth/verify", json={
        "phone": PHONE, "code": code, "device_id": device.installation_id,
        "device_public_key": device.public_b64, "device_name": "x", "platform": "ios"})
    assert r.status_code == 200, r.text


async def test_response_is_identical_for_linked_and_unlinked(client, bot):
    await _link(client)
    linked = await _request_otp(client, PHONE)
    unlinked = await _request_otp(client, "+998907654321")
    assert linked.json() == unlinked.json()  # kanal oshkor qilinmaydi


async def test_force_sms_and_fallbacks(client, container, bot):
    await _link(client)
    await _request_otp(client, channel="sms")
    assert len(container.sms.outbox) == 1  # "SMS orqali yuborish"
    container.kv.time_offset += 61
    bot.down = True  # Telegram ishlamayapti -> SMS
    await _request_otp(client)
    assert len(container.sms.outbox) == 2
    container.kv.time_offset += 61
    bot.down, bot.blocked = False, {USER_ID}  # bot bloklangan -> SMS va bog'lanish o'chadi
    await _request_otp(client)
    assert len(container.sms.outbox) == 3
    container.kv.time_offset += 61
    bot.blocked = set()
    await _request_otp(client)
    assert len(container.sms.outbox) == 4  # qayta ulanmaguncha SMS


async def test_foreign_contact_is_rejected(client, container, bot):
    # Boshqa odamning kontakt kartasini yuborish — kodini olishga urinish
    upd = _msg(contact={"phone_number": "998901234567", "user_id": 999})
    await _hook(client, upd)
    assert "o'z raqamingizni" in bot.sent[-1][1]
    upd = _msg(contact={"phone_number": "998901234567"})  # user_id yo'q (qo'lda kiritilgan)
    await _hook(client, upd)
    await _request_otp(client)
    assert len(container.sms.outbox) == 1  # ulanmagan — SMS


async def test_non_uzbek_number_and_group_chat_ignored(client, container, bot):
    await _link(client, phone="+79161234567")
    assert "+998" in bot.sent[-1][1]
    upd = _msg(contact={"phone_number": "998901234567", "user_id": USER_ID})
    upd["message"]["chat"]["type"] = "group"
    await _hook(client, upd)
    await _request_otp(client)
    assert len(container.sms.outbox) == 1


async def test_block_and_stop_unlink(client, container, bot):
    await _link(client)
    await _hook(client, {"update_id": 2, "my_chat_member": {
        "chat": {"id": USER_ID, "type": "private"},
        "new_chat_member": {"status": "kicked"}}})
    await _request_otp(client)
    assert len(container.sms.outbox) == 1
    await _link(client)
    await _hook(client, _msg(text="/stop"))
    container.kv.time_offset += 61
    await _request_otp(client)
    assert len(container.sms.outbox) == 2


async def test_one_telegram_account_one_number(client, container, bot):
    await _link(client, PHONE)
    await _link(client, "+998907654321")  # raqam almashdi — eski bog'lanish o'chadi
    await _request_otp(client, PHONE)
    assert len(container.sms.outbox) == 1


async def test_webhook_requires_secret(client, bot):
    assert (await _hook(client, _msg(text="/start"), secret="wrong")).status_code == 404
    r = await client.post("/v1/telegram/webhook", json=_msg(text="/start"))
    assert r.status_code == 404
    assert bot.sent == []


async def test_webhook_disabled_without_bot(client, container, settings):
    settings.telegram_webhook_secret = SecretStr(SECRET)
    assert (await _hook(client, _msg(text="/start"))).status_code == 404


async def test_account_deletion_removes_link(client, container, bot):
    s = await login(client, container, PHONE)
    await _link(client)
    container.kv.time_offset += 61
    assert (await client.post("/v1/me/delete-code", headers=s.headers)).status_code == 200
    code = bot.sent[-1][1].split("kodi ")[1][:6]  # o'chirish kodi ham Telegram'dan
    r = await client.request("DELETE", "/v1/me", headers=s.headers, json={"code": code})
    assert r.status_code == 204
    container.kv.time_offset += 61
    before = len(container.sms.outbox)
    await _request_otp(client)
    assert len(container.sms.outbox) == before + 1


async def test_polling_mode_links_and_acknowledges_updates(client, container):
    import json

    import httpx

    from app.infrastructure.telegram.bot import TelegramBotClient
    from app.telegram_poll import poll

    calls: list[tuple[str, dict]] = []
    batches = [
        [{"update_id": 10, "message": {"chat": {"id": USER_ID, "type": "private"},
                                       "from": {"id": USER_ID, "language_code": "ru"},
                                       "text": "/start"}},
         {"update_id": 11, "message": "buzilgan"},
         {"update_id": 12, "message": {"chat": {"id": USER_ID, "type": "private"},
                                       "from": {"id": USER_ID, "language_code": "ru"},
                                       "contact": {"phone_number": "998901234567",
                                                   "user_id": USER_ID}}}],
        [],
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        method = request.url.path.rsplit("/", 1)[-1]
        body = json.loads(request.content)
        calls.append((method, body))
        if method == "getUpdates":
            return httpx.Response(200, json={"ok": True, "result": batches.pop(0)})
        return httpx.Response(200, json={"ok": True, "result": True})

    bot = TelegramBotClient("123:abc", client=httpx.AsyncClient(
        base_url="https://api.telegram.test/bot123:abc", transport=httpx.MockTransport(handler)))
    container.telegram = bot
    assert await poll(container, bot, max_rounds=2) == 3

    methods = [m for m, _ in calls]
    assert methods[0] == "deleteWebhook"
    polls = [b for m, b in calls if m == "getUpdates"]
    assert "offset" not in polls[0] and polls[1]["offset"] == 13  # tasdiqlangan
    replies = [b["text"] for m, b in calls if m == "sendMessage"]
    assert "Поделитесь номером" in replies[0] and "Готово" in replies[1]

    # Endi OTP kodi SMS emas, botdan
    container.kv.time_offset += 61
    await _request_otp(client)
    assert container.sms.outbox == []
    assert "код подтверждения" in [b for m, b in calls if m == "sendMessage"][-1]["text"]
