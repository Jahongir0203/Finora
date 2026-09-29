from datetime import timedelta

from app.jobs import purge, run
from tests.conftest import expense, login


async def test_purge_removes_expired_exports_and_old_idempotency_keys(client, container):
    s = await login(client, container, "+998903000001")
    await expense(client, s, 1000, "transport")
    r = await client.post("/v1/exports", headers=s.headers, json={
        "period": "yearly", "include": ["expense"], "format": "csv"})
    assert r.status_code == 202

    assert await purge(container) == {"exports": 0, "idempotency_keys": 0, "receipts": 0}

    real_now = container.clock.now

    class Later:
        def now(self):
            return real_now() + timedelta(hours=25)

    container.clock = Later()
    assert await purge(container) == {"exports": 1, "idempotency_keys": 1, "receipts": 0}


async def test_tick_runs_all_hourly_jobs(client, container):
    await login(client, container, "+998903000001")
    result = await run(container, "tick")
    assert {"exports", "idempotency_keys", "receipts", "exports_processed", "push_retried",
            "advanced", "payment_due_sent", "weekly_sent", "autosaved"} <= set(result)
    assert "failed" not in result.values()
