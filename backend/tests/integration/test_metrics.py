import httpx
from pydantic import SecretStr

from app.core.metrics import REGISTRY
from app.main import create_app
from tests.conftest import DeviceKey, last_code


def _value(name: str, **labels: str) -> float:
    return REGISTRY.get_sample_value(name, labels) or 0.0


async def _client(settings, container):
    app = create_app(settings, container)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="https://api.test")


async def test_metrics_require_token_and_count_security_events(settings, container):
    settings.metrics_token = SecretStr("scrape-token-123")
    before_invalid = _value("finora_security_events_total", event="otp_invalid")
    before_429 = _value("finora_rate_limited_total", scope="otp")

    async with await _client(settings, container) as c:
        device = DeviceKey()
        body = {"phone": "+998905000001", "installation_id": device.installation_id}
        await c.post("/v1/auth/otp", json=body)
        await c.post("/v1/auth/otp", json=body)  # 60 s ichida — 429
        wrong = "000000" if last_code(container) != "000000" else "111111"
        await c.post("/v1/auth/verify", json={**body, "code": wrong,
                                              "device_public_key": device.public_b64,
                                              "device_name": "x", "platform": "ios"})

        assert (await c.get("/metrics")).status_code == 401
        assert (await c.get("/metrics", headers={"Authorization": "Bearer wrong"})
                ).status_code == 401
        r = await c.get("/metrics", headers={"Authorization": "Bearer scrape-token-123"})
    assert r.status_code == 200
    assert "finora_security_events_total" in r.text
    assert "+998" not in r.text and "905000001" not in r.text  # label'larda PII yo'q
    assert _value("finora_rate_limited_total", scope="otp") == before_429 + 1
    assert _value("finora_security_events_total", event="otp_invalid") == before_invalid + 1


async def test_metrics_disabled_without_token(client):
    assert (await client.get("/metrics")).status_code == 404
