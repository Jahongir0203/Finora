import logging

import httpx

from app.main import create_app
from tests.conftest import last_code, login

PHONE = "+998901234567"


async def test_plain_http_rejected(settings, container):
    app = create_app(settings, container)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                                 base_url="http://api.test") as c:
        r = await c.get("/v1/goals")
    assert r.status_code == 403
    assert r.json()["code"] == "https_required"


async def test_security_headers(client):
    r = await client.get("/health")
    assert r.headers["strict-transport-security"] == "max-age=31536000; includeSubDomains"
    assert r.headers["x-content-type-options"] == "nosniff"
    assert "x-request-id" in r.headers


async def test_body_over_1mb_rejected(client):
    r = await client.post("/v1/auth/otp", content=b"x" * (1024 * 1024 + 1),
                          headers={"Content-Type": "application/json"})
    assert r.status_code == 413


async def test_error_format_has_no_internals(client):
    r = await client.post("/v1/auth/otp", json={"phone": 123})
    assert r.status_code == 422
    body = r.json()
    assert set(body) == {"code", "message", "request_id", "fields"}
    assert body["code"] == "validation_error"
    assert "phone" in body["fields"] and "device_id" in body["fields"]
    assert "Traceback" not in r.text

    r = await client.get("/v1/does-not-exist")
    assert r.status_code == 404
    assert set(r.json()) == {"code", "message", "request_id"}


async def test_logs_do_not_contain_phone_or_otp(client, container, caplog):
    from app.core.logging import JsonFormatter

    caplog.set_level(logging.DEBUG)
    s = await login(client, container, PHONE)
    code = last_code(container)
    await client.get("/v1/goals", headers=s.headers)
    # Maxsus: kimdir telefonni to'g'ridan-to'g'ri log qilsa ham formatter maskalaydi
    logging.getLogger("finora.test").info("user phone %s", PHONE)

    formatter = JsonFormatter()
    output = "\n".join(formatter.format(r) for r in caplog.records)
    assert PHONE not in output
    assert "901234567" not in output
    assert code not in output
    assert s.access not in output and s.refresh not in output
    assert "+998 90 *** ** 67" in output


async def test_error_message_follows_accept_language(client):
    r = await client.get("/v1/goals", headers={"Accept-Language": "ru-RU,ru;q=0.9"})
    assert r.status_code == 401
    assert r.json()["message"] == "Требуется авторизация"
    r = await client.get("/v1/goals", headers={"Accept-Language": "uz-Cyrl"})
    assert r.json()["message"] == "Авторизация талаб қилинади"
    r = await client.get("/v1/goals", headers={"Accept-Language": "en"})
    assert r.json()["message"] == "Authorization required"


async def test_health_and_ready(client):
    assert (await client.get("/health")).json() == {"status": "ok"}
    r = await client.get("/ready")
    assert r.status_code == 200 and r.json() == {"status": "ok", "db": True, "cache": True}


async def test_docs_csp_relaxed_only_for_swagger_in_dev(settings, container):
    import httpx

    from app.main import create_app

    settings.docs_enabled = True
    app = create_app(settings, container)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                                 base_url="https://api.test") as c:
        docs = await c.get("/docs")
        api = await c.get("/v1/goals")
    assert docs.status_code == 200 and "cdn.jsdelivr.net" in docs.headers[
        "content-security-policy"]
    assert api.headers["content-security-policy"].startswith("default-src 'none'")


def test_logs_never_contain_bot_token_or_http_urls(caplog):
    from app.core.logging import JsonFormatter, configure_logging

    configure_logging("INFO")
    token = "1234567890:AAFakeTokenForTestsOnly_abcdefghijklm"
    caplog.set_level(logging.INFO)
    logging.getLogger("httpx").info("HTTP Request: POST https://api.telegram.org/bot%s/x", token)
    logging.getLogger("finora.test").info("url https://api.telegram.org/bot%s/getMe", token)
    output = "\n".join(JsonFormatter().format(r) for r in caplog.records)
    assert token not in output and "AAFake" not in output
    assert logging.getLogger("httpx").getEffectiveLevel() >= logging.WARNING
