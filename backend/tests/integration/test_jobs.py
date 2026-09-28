from datetime import timedelta

from app.jobs import purge
from tests.conftest import idem, login


async def test_purge_removes_expired_exports_and_old_idempotency_keys(client, container):
    s = await login(client, container, "+998903000001")
    await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "kind": "expense", "amount": 1000, "category": "Taksi",
        "occurred_at": "2026-09-20T10:00:00+05:00"})
    assert (await client.post("/v1/exports", headers=s.headers, json={})).status_code == 201

    assert await purge(container) == {"exports": 0, "idempotency_keys": 0}

    real_now = container.clock.now

    class Later:
        def now(self):
            return real_now() + timedelta(hours=25)

    container.clock = Later()
    assert await purge(container) == {"exports": 1, "idempotency_keys": 1}
