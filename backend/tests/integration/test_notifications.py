import json

from app.domain.common.values import PhoneNumber
from tests.conftest import DeviceKey, login

PHONE = "+998904000001"
FCM_A = "fcm-token-device-a-0000000000"
FCM_B = "fcm-token-device-b-0000000000"


async def _register(client, s, token: str, provider: str = "fcm"):
    return await client.put("/v1/me/push-token", headers=s.headers,
                            json={"provider": provider, "token": token})


async def test_new_sign_in_notifies_other_devices(client, container):
    a = await login(client, container, PHONE)
    assert (await _register(client, a, FCM_A)).status_code == 204

    b = await login(client, container, PHONE)  # yangi qurilma
    await _register(client, b, FCM_B)

    sent = container.push.sent
    assert [t for t, _, _ in sent] == [FCM_A]  # yangi qurilmaning o'ziga emas
    _, _, body = sent[0]
    assert "Test phone" not in body  # qulflangan ekranda qurilma nomi ko'rinmaydi

    items = (await client.get("/v1/me/notifications", headers=a.headers)).json()
    assert items[0]["kind"] == "new_sign_in" and "Test phone" in items[0]["body"]


async def test_refresh_reuse_notifies_and_invalid_token_cleared(client, container):
    s = await login(client, container, PHONE)
    await _register(client, s, FCM_A)
    body = json.dumps({"refresh_token": s.refresh}).encode()

    def sign():
        return {"Content-Type": "application/json",
                **s.device.sign("POST", "/v1/auth/refresh", body)}

    assert (await client.post("/v1/auth/refresh", content=body, headers=sign())).status_code == 200
    container.push.invalid.add(FCM_A)
    r = await client.post("/v1/auth/refresh", content=body, headers=sign())  # reuse
    assert r.status_code == 401

    assert await _targets(container, PHONE) == []  # 410/UNREGISTERED token bazadan olindi


async def test_notifications_are_private_and_mark_read(client, container):
    a = await login(client, container, PHONE)
    await login(client, container, PHONE, DeviceKey())  # a'ga "yangi kirish" yozuvi
    other = await login(client, container, "+998904000002")
    nid = (await client.get("/v1/me/notifications", headers=a.headers)).json()[0]["id"]

    assert (await client.get("/v1/me/notifications", headers=other.headers)).json() == []
    r = await client.post(f"/v1/me/notifications/{nid}/read", headers=other.headers)
    assert r.status_code == 404
    r = await client.post(f"/v1/me/notifications/{nid}/read", headers=a.headers)
    assert r.status_code == 204
    assert (await client.get("/v1/me/notifications", headers=a.headers)).json()[0]["read_at"]


async def test_push_token_moves_between_accounts_on_same_phone(client, container):
    a = await login(client, container, PHONE)
    await _register(client, a, FCM_A)
    other = await login(client, container, "+998904000002")
    await _register(client, other, FCM_A)  # bir telefon, boshqa akkaunt

    assert await _targets(container, PHONE) == []  # birinchi akkaunt bu telefonga yubormaydi
    assert len(await _targets(container, "+998904000002")) == 1


async def _targets(container, phone: str):
    async with container.uow() as uow:
        user = await uow.users.get_by_phone_index(
            container.hasher.phone_index(PhoneNumber(phone)))
        return await uow.push_tokens.targets(user.id, active_only=False)


async def test_push_token_validation(client, container):
    s = await login(client, container, PHONE)
    assert (await _register(client, s, "short")).status_code == 422
    assert (await _register(client, s, "x" * 20 + "<script>")).status_code == 422
    assert (await _register(client, s, FCM_A, provider="sms")).status_code == 422
    assert (await client.delete("/v1/me/push-token", headers=s.headers)).status_code == 204
