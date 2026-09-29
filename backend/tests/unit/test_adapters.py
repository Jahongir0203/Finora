"""Tashqi provayder adapterlari — tarmoqsiz (httpx.MockTransport, botocore Stubber)."""

import json

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from app.application.common.interfaces import PushSendResult
from app.core.config import Settings
from app.domain.common.errors import ServiceUnavailableError
from app.domain.common.values import PhoneNumber
from app.domain.notifications.entities import PushProvider
from app.infrastructure.push.apns import ApnsSender
from app.infrastructure.push.fcm import FcmSender
from app.infrastructure.sms.eskiz import EskizSmsSender

PHONE = PhoneNumber("+998901234567")


def _eskiz(handler) -> EskizSmsSender:
    settings = Settings(env="test", eskiz_email="ops@finora.uz", eskiz_password="pw")
    client = httpx.AsyncClient(base_url="https://eskiz.test/api",
                               transport=httpx.MockTransport(handler))
    return EskizSmsSender(settings, client)


async def test_eskiz_logs_in_once_and_sends():
    calls: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        calls.append(req.url.path)
        if req.url.path.endswith("/auth/login"):
            return httpx.Response(200, json={"data": {"token": "T1"}})
        assert req.headers["Authorization"] == "Bearer T1"
        form = dict(x.split("=") for x in req.content.decode().split("&"))
        assert form["mobile_phone"] == "998901234567" and form["from"] == "4546"
        return httpx.Response(200, json={"status": "waiting"})

    sms = _eskiz(handler)
    await sms.send(PHONE, "Finora: kod 123456")
    await sms.send(PHONE, "Finora: kod 654321")
    assert calls.count("/api/auth/login") == 1


async def test_eskiz_relogins_on_401():
    tokens = iter(["OLD", "NEW"])

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/auth/login"):
            return httpx.Response(200, json={"data": {"token": next(tokens)}})
        ok = req.headers["Authorization"] == "Bearer NEW"
        return httpx.Response(200 if ok else 401)

    await _eskiz(handler).send(PHONE, "x")


@pytest.mark.parametrize("fail", ["login", "send", "network"])
async def test_eskiz_errors_become_503_without_leaking(fail, caplog):
    def handler(req: httpx.Request) -> httpx.Response:
        if fail == "network":
            raise httpx.ConnectError("boom")
        if req.url.path.endswith("/auth/login"):
            return httpx.Response(401 if fail == "login" else 200, json={"data": {"token": "T"}})
        return httpx.Response(500, text="provider internal details")

    with pytest.raises(ServiceUnavailableError):
        await _eskiz(handler).send(PHONE, "Finora: kod 123456")
    assert "123456" not in caplog.text and "provider internal" not in caplog.text


def test_eskiz_requires_credentials():
    with pytest.raises(ValueError):
        EskizSmsSender(Settings(env="test"))


def _service_account() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()
    return json.dumps({"project_id": "finora-test", "client_email": "fcm@finora.iam",
                       "private_key": pem, "token_uri": "https://oauth.test/token"})


async def test_fcm_send_and_unregistered():
    oauth_calls = 0

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal oauth_calls
        if req.url.host == "oauth.test":
            oauth_calls += 1
            return httpx.Response(200, json={"access_token": "ya29", "expires_in": 3600})
        assert req.url.path == "/v1/projects/finora-test/messages:send"
        assert req.headers["Authorization"] == "Bearer ya29"
        token = json.loads(req.content)["message"]["token"]
        if token == "dead":
            return httpx.Response(404, json={"error": {"status": "NOT_FOUND",
                                                       "details": [{"errorCode": "UNREGISTERED"}]}})
        return httpx.Response(200, json={"name": "projects/x/messages/1"})

    fcm = FcmSender(_service_account(), httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    assert await fcm.send(PushProvider.FCM, "alive", "t", "b") is PushSendResult.OK
    assert await fcm.send(PushProvider.FCM, "dead", "t", "b") is PushSendResult.INVALID_TOKEN
    assert oauth_calls == 1  # access token keshlanadi


async def test_apns_send_and_gone():
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.headers["apns-topic"] == "uz.finora.app"
        assert req.headers["authorization"].startswith("bearer ")
        if req.url.path.endswith("/deadbeef"):
            return httpx.Response(410, json={"reason": "Unregistered"})
        return httpx.Response(200)

    apns = ApnsSender("TEAM123456", "KEY1234567", pem, "uz.finora.app",
                      client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    assert await apns.send(PushProvider.APNS, "abc123", "t", "b") is PushSendResult.OK
    assert await apns.send(PushProvider.APNS, "deadbeef", "t", "b") is PushSendResult.INVALID_TOKEN
    # Path injection urinishi — so'rov yuborilmaydi
    assert await apns.send(PushProvider.APNS, "../../x", "t", "b") is PushSendResult.INVALID_TOKEN


async def test_s3_storage_encrypts_and_presigns():
    import boto3
    from botocore.config import Config
    from botocore.stub import ANY, Stubber

    from app.infrastructure.storage.s3 import S3FileStorage

    client = boto3.client("s3", region_name="us-east-1", aws_access_key_id="AK",
                          aws_secret_access_key="SK",
                          config=Config(signature_version="s3v4"))
    settings = Settings(env="test", s3_bucket="finora-private", s3_kms_key_id="kms-1")
    storage = S3FileStorage(settings, client)
    with Stubber(client) as stub:
        stub.add_response("put_object", {}, {
            "Bucket": "finora-private", "Key": "receipts/u/r.jpg", "Body": ANY,
            "ContentType": "image/jpeg", "ServerSideEncryption": "aws:kms", "SSEKMSKeyId": "kms-1",
        })
        await storage.put("receipts/u/r.jpg", b"x", "image/jpeg")
        stub.add_client_error("get_object", service_error_code="NoSuchKey", http_status_code=404)
        assert await storage.get("missing") is None

    url = await storage.presigned_get_url("receipts/u/r.jpg", 300)
    assert url and "X-Amz-Expires=300" in url and "X-Amz-Signature=" in url


async def test_phone_key_rotation(client, container, settings):
    import base64

    from pydantic import SecretStr

    from app.domain.common.values import PhoneNumber
    from app.infrastructure.security.cipher import AesGcmPhoneCipher
    from app.jobs import run
    from tests.conftest import login

    s = await login(client, container, "+998909990001")
    old_key = settings.field_encryption_key.get_secret_value()
    rotated = settings.model_copy(update={
        "field_encryption_key": SecretStr(base64.b64encode(b"n" * 32).decode()),
        "field_encryption_key_version": 2,
        "field_encryption_keys_previous": SecretStr(f"1:{old_key}"),
    })
    container.cipher = AesGcmPhoneCipher(rotated)
    assert (await run(container, "reencrypt-phones"))["reencrypted"] == 1
    assert (await run(container, "reencrypt-phones"))["reencrypted"] == 0
    only_new = AesGcmPhoneCipher(rotated.model_copy(update={
        "field_encryption_keys_previous": None}))
    async with container.uow() as uow:
        user = await uow.users.get_by_phone_index(
            container.hasher.phone_index(PhoneNumber("+998909990001")))
    assert user.phone_ciphertext[0] == 2
    assert only_new.decrypt(user.phone_ciphertext).value == "+998909990001"
    del s


async def test_cbu_rates_parsing_with_nominal():
    from decimal import Decimal

    import httpx

    from app.infrastructure.rates.cbu import CbuRatesProvider

    payload = [{"Ccy": "USD", "Rate": "11806.97", "Nominal": "1"},
               {"Ccy": "KRW", "Rate": "8.5", "Nominal": "1"},
               {"Ccy": "KZT", "Rate": "267.8", "Nominal": "10"},
               {"Ccy": "EUR", "Rate": "bad", "Nominal": "1"}]
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    provider = CbuRatesProvider("https://cbu.test/json/",
                                client=httpx.AsyncClient(transport=transport))
    assert await provider.fetch() == {"USD": Decimal("11806.9700"),
                                      "KZT": Decimal("26.7800")}


async def test_sms_fallback_uses_secondary_on_503():
    from app.domain.common.errors import ServiceUnavailableError
    from app.domain.common.values import PhoneNumber
    from app.infrastructure.sms.console import InMemorySmsSender
    from app.infrastructure.sms.fallback import FallbackSmsSender

    class Down:
        async def send(self, phone, text):
            raise ServiceUnavailableError()

    backup = InMemorySmsSender()
    await FallbackSmsSender(Down(), backup).send(PhoneNumber("+998901234567"), "kod 123456")
    assert len(backup.outbox) == 1


async def test_playmobile_request_shape():
    import json

    import httpx
    from pydantic import SecretStr

    from app.core.config import Settings
    from app.domain.common.values import PhoneNumber
    from app.infrastructure.sms.playmobile import PlayMobileSmsSender

    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.content)
        seen["auth"] = request.headers["authorization"]
        return httpx.Response(200)

    settings = Settings(env="test", playmobile_login="finora",
                        playmobile_password=SecretStr("pw"))
    sender = PlayMobileSmsSender(settings, client=httpx.AsyncClient(
        base_url="https://pm.test", transport=httpx.MockTransport(handler),
        auth=("finora", "pw")))
    await sender.send(PhoneNumber("+998901234567"), "Finora: kod 123456")
    msg = seen["body"]["messages"][0]
    assert msg["recipient"] == "998901234567" and msg["sms"]["content"]["text"].endswith("123456")
    assert seen["auth"].startswith("Basic ")
