"""Activity (BE-503/504), sync (BE-302), statistika (BE-801)."""

from datetime import UTC, datetime, timedelta

from tests.conftest import expense, idem, income, login

PHONE = "+998907770001"


class FixedClock:
    def __init__(self, at: datetime) -> None:
        self.at = at

    def now(self) -> datetime:
        return self.at


async def test_search_filters_and_empty_result(client, container):
    s = await login(client, container, PHONE)
    await expense(client, s, 45_000, "food", title="Evos cafe")
    await expense(client, s, 20_000, "transport", title="Yandex Go", note="uyga")
    await income(client, s, 3_000_000, title="Oylik")

    def titles(r):
        return [i["title"] for i in r.json()["items"]]

    r = await client.get("/v1/transactions?q=evos", headers=s.headers)
    assert titles(r) == ["Evos cafe"]
    r = await client.get("/v1/transactions?q=UYGA", headers=s.headers)  # izoh, katta harf
    assert titles(r) == ["Yandex Go"]
    r = await client.get("/v1/transactions?q=Transport", headers=s.headers)  # kategoriya nomi
    assert titles(r) == ["Yandex Go"]
    r = await client.get("/v1/transactions?type=income", headers=s.headers)
    assert titles(r) == ["Oylik"]
    r = await client.get("/v1/transactions?category_id=food", headers=s.headers)
    assert titles(r) == ["Evos cafe"]
    r = await client.get("/v1/transactions?q=%25", headers=s.headers)  # LIKE maxsus belgisi
    assert r.status_code == 200 and titles(r) == []
    r = await client.get("/v1/transactions?q=nothing", headers=s.headers)
    assert r.status_code == 200 and r.json() == {"items": [], "next_cursor": None, "groups": []}


async def test_cursor_pagination_and_daily_groups(client, container):
    s = await login(client, container, PHONE)
    tz = "+05:00"
    for day, amount in ((27, 10_000), (27, 5_000), (28, 7_000), (28, 3_000), (28, 1_000)):
        await expense(client, s, amount, "food", occurred_at=f"2026-09-{day}T12:00:00{tz}")
    await income(client, s, 50_000, occurred_at="2026-09-28T09:00:00+05:00")

    first = (await client.get("/v1/transactions?limit=5", headers=s.headers)).json()
    assert len(first["items"]) == 5 and first["next_cursor"]
    # Guruh summasi sahifadagi yozuvlar emas, butun kun bo'yicha (27-da 2 ta, sahifada 1 ta)
    assert first["groups"] == [{"date": "2026-09-28", "net": 39_000},
                               {"date": "2026-09-27", "net": -15_000}]
    second = (await client.get(f"/v1/transactions?limit=5&cursor={first['next_cursor']}",
                               headers=s.headers)).json()
    assert len(second["items"]) == 1 and second["next_cursor"] is None
    ids = [i["id"] for i in first["items"] + second["items"]]
    assert len(set(ids)) == 6
    assert (await client.get("/v1/transactions?cursor=garbage",
                             headers=s.headers)).status_code == 422
    r = await client.get("/v1/transactions?from=2026-09-28&to=2026-09-28", headers=s.headers)
    assert len(r.json()["items"]) == 4


async def test_patch_and_soft_delete_recalculate_balance(client, container):
    s = await login(client, container, PHONE)
    tx = await expense(client, s, 40_000, "food")
    r = await client.patch(f"/v1/transactions/{tx['id']}", headers=s.headers,
                           json={"amount": 25_000, "category_id": "groceries", "note": None})
    assert r.status_code == 200
    assert (r.json()["amount"], r.json()["category_id"]) == (25_000, "groceries")
    bad = await client.patch(f"/v1/transactions/{tx['id']}", headers=s.headers,
                             json={"category_id": "salary"})
    assert bad.json()["code"] == "category_type_mismatch"
    assert (await client.get("/v1/home", headers=s.headers)).json()["balance"]["total"] == -25_000
    assert (await client.delete(f"/v1/transactions/{tx['id']}",
                                headers=s.headers)).status_code == 204
    assert (await client.get(f"/v1/transactions/{tx['id']}", headers=s.headers)).status_code == 404
    assert (await client.get("/v1/home", headers=s.headers)).json()["balance"]["total"] == 0


async def test_sync_returns_changes_and_deletions(client, container):
    s = await login(client, container, PHONE)
    since = datetime.now(UTC) - timedelta(seconds=1)
    kept = await expense(client, s, 10_000, "food")
    gone = await expense(client, s, 20_000, "food")
    await client.delete(f"/v1/transactions/{gone['id']}", headers=s.headers)
    await client.post("/v1/goals", headers={**s.headers, **idem()},
                      json={"name": "Car", "target": 100_000})
    r = await client.get("/v1/sync", params={"since": since.isoformat()}, headers=s.headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert [t["id"] for t in body["transactions"]["changed"]] == [kept["id"]]
    assert body["transactions"]["deleted"] == [gone["id"]]
    assert len(body["goals"]["changed"]) == 1
    assert len(body["accounts"]["changed"]) == 1  # standart "Cash" avtomatik yaratildi
    later = await client.get("/v1/sync", params={"since": body["server_time"]},
                             headers=s.headers)
    assert later.json()["transactions"] == {"changed": [], "deleted": []}


async def test_stats_month_week_year(client, container):
    container.clock = FixedClock(datetime(2026, 9, 28, 7, 0, tzinfo=UTC))
    s = await login(client, container, PHONE)
    for day, cat, amount in ((2, "food", 300_000), (9, "groceries", 500_000),
                             (15, "food", 200_000), (28, "transport", 100_000)):
        await expense(client, s, amount, cat, occurred_at=f"2026-09-{day:02d}T12:00:00+05:00")
    await expense(client, s, 1_000_000, "food", occurred_at="2026-08-10T12:00:00+05:00")
    await income(client, s, 5_000_000, occurred_at="2026-09-05T12:00:00+05:00")

    m = (await client.get("/v1/stats?period=month", headers=s.headers)).json()
    assert m["total_spent"] == 1_100_000
    assert [b["label"] for b in m["bars"]] == ["W1", "W2", "W3", "W4", "W5"]
    # W1 1-7, W2 8-14, W3 15-21, W4 22-28, W5 29-30
    assert [b["value"] for b in m["bars"]] == [300_000, 500_000, 200_000, 100_000, 0]
    assert [b["current"] for b in m["bars"]] == [False, False, False, True, False]
    assert m["change_pct"] == 10  # avgust 1 000 000 -> sentabr 1 100 000
    assert [b["category_id"] for b in m["breakdown"]] == ["food", "groceries", "transport"]
    assert sum(b["pct"] for b in m["breakdown"]) == 100
    assert m["has_enough_data"] is True

    w = (await client.get("/v1/stats?period=week", headers=s.headers)).json()
    assert [b["label"] for b in w["bars"]] == ["M", "T", "W", "T", "F", "S", "S"]
    assert w["bars"][0]["value"] == 100_000 and w["bars"][0]["current"] is True
    assert w["bars"][1]["future"] is True

    y = (await client.get("/v1/stats?period=year", headers=s.headers)).json()
    assert len(y["bars"]) == 12 and y["bars"][7]["value"] == 1_000_000
    assert all(b["value"] == 0 for b in y["bars"][9:])


async def test_stats_not_enough_data_for_new_user(client, container):
    s = await login(client, container, PHONE)
    await expense(client, s, 1000, "food")
    r = (await client.get("/v1/stats", headers=s.headers)).json()
    assert r["has_enough_data"] is False and r["change_pct"] is None


def test_percentages_always_sum_to_100():
    from app.application.stats.use_cases import percentages

    for amounts in ([1, 1, 1], [333, 333, 334], [5, 0, 0], [1, 2, 3, 4, 5, 6, 7],
                    [999_999, 1]):
        assert sum(percentages(amounts)) == 100, amounts
    assert percentages([]) == [] and percentages([0, 0]) == [0, 0]
