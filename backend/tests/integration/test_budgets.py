from datetime import UTC, datetime

from tests.conftest import idem, login

PHONE_A = "+998906000001"
PHONE_B = "+998906000002"


async def _expense(client, s, amount: int, category: str, when: str) -> None:
    r = await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "kind": "expense", "amount": amount, "category": category, "occurred_at": when})
    assert r.status_code == 201, r.text


async def test_budget_spent_is_computed_for_current_month(client, container):
    s = await login(client, container, PHONE_A)
    now = datetime.now(UTC)
    this_month = now.isoformat()
    await _expense(client, s, 120_000, "Oziq-ovqat", this_month)
    await _expense(client, s, 30_000, "Oziq-ovqat", this_month)
    await _expense(client, s, 999_000, "Oziq-ovqat", "2020-01-15T10:00:00+05:00")  # eski oy
    await _expense(client, s, 50_000, "Taksi", this_month)

    r = await client.post("/v1/budgets", headers={**s.headers, **idem()},
                          json={"category": "Oziq-ovqat", "monthly_limit": 1_000_000})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["spent"] == 150_000 and body["remaining"] == 850_000


async def test_budget_client_cannot_set_spent_and_duplicate_conflicts(client, container):
    s = await login(client, container, PHONE_A)
    body = {"category": "Taksi", "monthly_limit": 200_000}
    r = await client.post("/v1/budgets", headers={**s.headers, **idem()},
                          json={**body, "spent": 0})
    assert r.status_code == 422  # mass assignment
    assert (await client.post("/v1/budgets", headers={**s.headers, **idem()},
                              json=body)).status_code == 201
    r = await client.post("/v1/budgets", headers={**s.headers, **idem()}, json=body)
    assert r.status_code == 409 and r.json()["code"] == "conflict"


async def test_budget_idor(client, container):
    a = await login(client, container, PHONE_A)
    b = await login(client, container, PHONE_B)
    bid = (await client.post("/v1/budgets", headers={**a.headers, **idem()},
                             json={"category": "Kafe", "monthly_limit": 100_000})).json()["id"]
    for method, extra in (("GET", {}), ("PATCH", {"json": {"monthly_limit": 1}}),
                          ("DELETE", {})):
        resp = await client.request(method, f"/v1/budgets/{bid}", headers=b.headers, **extra)
        assert resp.status_code == 404, method
    assert (await client.get("/v1/budgets", headers=b.headers)).json() == []
    r = await client.patch(f"/v1/budgets/{bid}", headers=a.headers, json={"monthly_limit": 5})
    assert r.status_code == 200 and r.json()["monthly_limit"] == 5


def test_month_bounds_use_tashkent_time():
    from app.domain.budgets.entities import month_bounds

    # 31-dekabr 20:00 UTC = 1-yanvar 01:00 Toshkent — allaqachon yangi oy
    start, end = month_bounds(datetime(2026, 12, 31, 20, 0, tzinfo=UTC))
    assert start == datetime(2026, 12, 31, 19, 0, tzinfo=UTC)
    assert end == datetime(2027, 1, 31, 19, 0, tzinfo=UTC)
