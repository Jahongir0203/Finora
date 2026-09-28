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
