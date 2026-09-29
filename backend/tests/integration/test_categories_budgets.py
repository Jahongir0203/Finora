"""Kategoriyalar (BE-1501) va byudjetlar (BE-1001)."""

from datetime import UTC, datetime

from tests.conftest import expense, idem, income, login

PHONE = "+998905550001"


async def test_system_categories_listed_and_localized(client, container):
    s = await login(client, container, PHONE)
    cats = (await client.get("/v1/categories", headers=s.headers)).json()
    ids = [c["id"] for c in cats]
    assert ids == ["groceries", "food", "transport", "bills", "health", "shopping", "housing",
                   "subs", "salary", "transfer"]
    assert all(c["is_system"] and c["monthly_limit"] is None for c in cats)
    r = await client.patch("/v1/me/settings", headers=s.headers, json={"language": "ru"})
    assert r.json()["language"] == "ru"
    cats = (await client.get("/v1/categories?type=income", headers=s.headers)).json()
    assert [c["name"] for c in cats] == ["Зарплата", "Переводы"]


async def test_user_category_crud_and_duplicate_name(client, container):
    s = await login(client, container, PHONE)
    body = {"name": "Coffee", "icon": "coffee", "color": "#14b8a6", "type": "expense",
            "monthly_limit": 300_000}
    r = await client.post("/v1/categories", headers={**s.headers, **idem()}, json=body)
    assert r.status_code == 201
    cat = r.json()
    assert cat["color"] == "#14B8A6" and cat["monthly_limit"] == 300_000
    dup = await client.post("/v1/categories", headers={**s.headers, **idem()},
                            json={**body, "name": "coffee"})
    assert dup.status_code == 409
    bad = await client.post("/v1/categories", headers={**s.headers, **idem()},
                            json={**body, "name": "X", "icon": "rocket"})
    assert bad.status_code == 422 and bad.json()["fields"] == ["icon"]
    empty = await client.post("/v1/categories", headers={**s.headers, **idem()},
                              json={**body, "name": "  "})
    assert empty.json()["code"] == "category_name_required"

    r = await client.patch(f"/v1/categories/{cat['id']}", headers=s.headers,
                           json={"name": "Kofe", "monthly_limit": None})
    assert r.json()["name"] == "Kofe" and r.json()["monthly_limit"] is None


async def test_system_category_only_limit_and_name_override(client, container):
    s = await login(client, container, PHONE)
    r = await client.patch("/v1/categories/food", headers=s.headers,
                           json={"monthly_limit": 1_000_000, "name": "Ovqat"})
    assert r.status_code == 200
    assert r.json()["monthly_limit"] == 1_000_000 and r.json()["name"] == "Ovqat"
    r = await client.patch("/v1/categories/food", headers=s.headers, json={"icon": "coffee"})
    assert r.status_code == 422
    assert (await client.delete("/v1/categories/food", headers=s.headers)).status_code == 422


async def test_delete_category_with_transactions_requires_reassign(client, container):
    s = await login(client, container, PHONE)
    cat = (await client.post("/v1/categories", headers={**s.headers, **idem()}, json={
        "name": "Gym", "icon": "dumbbell", "color": "#EF4444", "type": "expense"})).json()
    tx = await expense(client, s, 90_000, cat["id"])
    r = await client.delete(f"/v1/categories/{cat['id']}", headers=s.headers)
    assert r.status_code == 409 and r.json()["code"] == "category_in_use"
    r = await client.request("DELETE", f"/v1/categories/{cat['id']}", headers=s.headers,
                             json={"reassign_to": "salary"})
    assert r.status_code == 422  # income kategoriyaga o'tkazib bo'lmaydi
    r = await client.request("DELETE", f"/v1/categories/{cat['id']}", headers=s.headers,
                             json={"reassign_to": "health"})
    assert r.status_code == 204
    moved = (await client.get(f"/v1/transactions/{tx['id']}", headers=s.headers)).json()
    assert moved["category_id"] == "health"


async def test_transaction_category_must_match_type(client, container):
    s = await login(client, container, PHONE)
    r = await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "type": "expense", "amount": 1000, "category_id": "salary"})
    assert r.status_code == 422 and r.json()["code"] == "category_type_mismatch"
    r = await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "type": "income", "amount": 1000, "category_id": "food"})
    assert r.json()["code"] == "category_type_mismatch"
    r = await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "type": "expense", "amount": 1000, "category_id": "no-such"})
    assert r.status_code == 422


async def test_budgets_status_and_new_user_has_none(client, container):
    s = await login(client, container, PHONE)
    assert (await client.get("/v1/budgets", headers=s.headers)).json() == []
    for cat, limit in (("food", 100_000), ("transport", 100_000), ("groceries", 100_000)):
        await client.patch(f"/v1/categories/{cat}", headers=s.headers,
                           json={"monthly_limit": limit})
    await expense(client, s, 50_000, "food")
    await expense(client, s, 80_000, "transport")
    await expense(client, s, 120_000, "groceries")
    await income(client, s, 500_000)
    budgets = {b["category_id"]: b for b in
               (await client.get("/v1/budgets", headers=s.headers)).json()}
    assert budgets["food"]["status"] == "normal" and budgets["food"]["left"] == 50_000
    assert budgets["transport"]["status"] == "warning" and budgets["transport"]["pct"] == 80
    assert budgets["groceries"]["status"] == "over" and budgets["groceries"]["left"] == -20_000
    other = (await client.get("/v1/budgets?month=2020-01", headers=s.headers)).json()
    assert all(b["spent"] == 0 for b in other) and len(other) == 3  # limit saqlanadi


async def test_budget_notifications_75_and_100_once_per_month(client, container):
    s = await login(client, container, PHONE)
    await client.patch("/v1/categories/food", headers=s.headers, json={"monthly_limit": 100_000})
    await expense(client, s, 50_000, "food")
    await expense(client, s, 30_000, "food")  # 80% -> ogohlantirish
    await expense(client, s, 5_000, "food")  # yana 75%+ — takror yo'q
    await expense(client, s, 20_000, "food")  # 105% -> oshdi
    await expense(client, s, 1_000, "food")
    items = (await client.get("/v1/notifications", headers=s.headers)).json()["items"]
    budget = [i for i in items if i["type"] == "budget_exceeded"]
    assert len(budget) == 2
    assert budget[0]["deep_link"] == "/budgets"


def test_month_bounds_use_local_timezone():
    from zoneinfo import ZoneInfo

    from app.domain.common.time import month_bounds

    # 31-dekabr 20:00 UTC = 1-yanvar 01:00 Toshkent — yangi oy
    start, end = month_bounds(datetime(2026, 12, 31, 20, 0, tzinfo=UTC),
                              ZoneInfo("Asia/Tashkent"))
    assert start == datetime(2026, 12, 31, 19, 0, tzinfo=UTC)
    assert end == datetime(2027, 1, 31, 19, 0, tzinfo=UTC)
