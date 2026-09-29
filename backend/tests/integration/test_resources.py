"""02-backend.md qabul mezonlari: IDOR -> 404, UUIDv7, idempotency, withdraw > saved,
mass assignment, CSV formula injection, akkaunt o'chirish."""

import asyncio
import uuid

from tests.conftest import expense, idem, last_code, login


async def _goal(client, s, target=1_000_000):
    r = await client.post("/v1/goals", json={"name": "Mashina", "target": target},
                          headers={**s.headers, **idem()})
    assert r.status_code == 201, r.text
    return r.json()


async def test_idor_returns_404_for_foreign_resources(client, container):
    alice = await login(client, container, "+998901111111")
    bob = await login(client, container, "+998902222222")
    goal = await _goal(client, alice)
    tx = await expense(client, alice, 5000, "food")
    acc = (await client.get("/v1/accounts", headers=alice.headers)).json()["items"][0]
    rem = (await client.post("/v1/reminders", headers={**alice.headers, **idem()}, json={
        "title": "Internet", "category_id": "bills", "amount": 100_000,
        "due_date": "2026-10-05", "repeat": "monthly"})).json()
    cat = (await client.post("/v1/categories", headers={**alice.headers, **idem()}, json={
        "name": "Coffee", "icon": "coffee", "color": "#14B8A6", "type": "expense"})).json()
    exp = (await client.post("/v1/exports", headers=alice.headers, json={
        "period": "monthly", "include": ["expense"], "format": "csv"})).json()

    checks = [
        ("GET", f"/v1/goals/{goal['id']}", None),
        ("PATCH", f"/v1/goals/{goal['id']}", {"name": "hack"}),
        ("DELETE", f"/v1/goals/{goal['id']}", None),
        ("POST", f"/v1/goals/{goal['id']}/deposits", {"amount": 1}),
        ("POST", f"/v1/goals/{goal['id']}/withdrawals", {"amount": 1}),
        ("GET", f"/v1/goals/{goal['id']}/history", None),
        ("GET", f"/v1/transactions/{tx['id']}", None),
        ("PATCH", f"/v1/transactions/{tx['id']}", {"amount": 1}),
        ("DELETE", f"/v1/transactions/{tx['id']}", None),
        ("GET", f"/v1/accounts/{acc['id']}", None),
        ("PATCH", f"/v1/accounts/{acc['id']}", {"name": "hack"}),
        ("POST", f"/v1/accounts/{acc['id']}/freeze", None),
        ("DELETE", f"/v1/accounts/{acc['id']}", None),
        ("GET", f"/v1/reminders/{rem['id']}", None),
        ("POST", f"/v1/reminders/{rem['id']}/pay", {}),
        ("DELETE", f"/v1/reminders/{rem['id']}", None),
        ("PATCH", f"/v1/categories/{cat['id']}", {"name": "hack"}),
        ("DELETE", f"/v1/categories/{cat['id']}", None),
        ("GET", f"/v1/exports/{exp['id']}", None),
    ]
    for method, url, body in checks:
        r = await client.request(method, url, json=body, headers={**bob.headers, **idem()})
        assert r.status_code == 404, (method, url, r.status_code, r.text)

    # Mavjud bo'lmagan va begona resurs javobi bir xil
    missing = await client.get(f"/v1/goals/{uuid.uuid4()}", headers=bob.headers)
    foreign = await client.get(f"/v1/goals/{goal['id']}", headers=bob.headers)
    assert missing.json()["code"] == foreign.json()["code"] == "not_found"

    # Begona hisobga yozuv qo'shib bo'lmaydi
    r = await client.post("/v1/transactions", headers={**bob.headers, **idem()}, json={
        "type": "expense", "amount": 1, "category_id": "food", "account_id": acc["id"]})
    assert r.status_code == 422
    devices = (await client.get("/v1/me/devices", headers=alice.headers)).json()
    r = await client.delete(f"/v1/me/devices/{devices[0]['id']}", headers=bob.headers)
    assert r.status_code == 404
    # Alice resurslari buzilmagan
    assert (await client.get(f"/v1/goals/{goal['id']}", headers=alice.headers)).status_code == 200
    assert (await client.get(f"/v1/transactions/{tx['id']}",
                             headers=alice.headers)).status_code == 200


async def test_ids_are_uuid7(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    tx = await expense(client, s)
    assert uuid.UUID(goal["id"]).version == 7
    assert uuid.UUID(tx["id"]).version == 7
    assert uuid.UUID(tx["account_id"]).version == 7


async def test_same_idempotency_key_creates_single_deposit(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    headers = {**s.headers, **idem()}
    r1 = await client.post(f"/v1/goals/{goal['id']}/deposits", json={"amount": 50_000},
                           headers=headers)
    r2 = await client.post(f"/v1/goals/{goal['id']}/deposits", json={"amount": 50_000},
                           headers=headers)
    assert r1.status_code == r2.status_code == 201
    assert r1.json() == r2.json()
    saved = (await client.get(f"/v1/goals/{goal['id']}", headers=s.headers)).json()["saved"]
    assert saved == 50_000


async def test_same_idempotency_key_creates_single_transaction(client, container):
    s = await login(client, container, "+998901111111")
    headers = {**s.headers, **idem()}
    body = {"type": "expense", "amount": 7000, "category_id": "food",
            "client_created_at": "2026-09-20T10:00:00+05:00"}
    r1 = await client.post("/v1/transactions", json=body, headers=headers)
    r2 = await client.post("/v1/transactions", json=body, headers=headers)
    assert r1.json() == r2.json()
    page = (await client.get("/v1/transactions", headers=s.headers)).json()
    assert len(page["items"]) == 1


async def test_idempotency_key_reuse_with_other_body_conflicts(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    headers = {**s.headers, **idem()}
    await client.post(f"/v1/goals/{goal['id']}/deposits", json={"amount": 1}, headers=headers)
    r = await client.post(f"/v1/goals/{goal['id']}/deposits", json={"amount": 2},
                          headers=headers)
    assert r.status_code == 409


async def test_idempotency_key_required(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    r = await client.post(f"/v1/goals/{goal['id']}/deposits", json={"amount": 1},
                          headers=s.headers)
    assert r.status_code == 400
    assert r.json()["code"] == "idempotency_key_required"


async def test_withdraw_more_than_saved_is_422(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    await client.post(f"/v1/goals/{goal['id']}/deposits", json={"amount": 100},
                      headers={**s.headers, **idem()})
    r = await client.post(f"/v1/goals/{goal['id']}/withdrawals", json={"amount": 101},
                          headers={**s.headers, **idem()})
    assert r.status_code == 422
    assert r.json()["code"] == "insufficient_funds"
    ok = await client.post(f"/v1/goals/{goal['id']}/withdrawals", json={"amount": 100},
                           headers={**s.headers, **idem()})
    assert ok.status_code == 201
    assert ok.json()["saved"] == 0


async def test_parallel_withdrawals_cannot_exceed_saved(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    await client.post(f"/v1/goals/{goal['id']}/deposits", json={"amount": 100_000},
                      headers={**s.headers, **idem()})
    results = await asyncio.gather(*(
        client.post(f"/v1/goals/{goal['id']}/withdrawals", json={"amount": 60_000},
                    headers={**s.headers, **idem()}) for _ in range(2)))
    assert sorted(r.status_code for r in results) == [201, 422]
    saved = (await client.get(f"/v1/goals/{goal['id']}", headers=s.headers)).json()["saved"]
    assert saved == 40_000


async def test_mass_assignment_rejected(client, container):
    s = await login(client, container, "+998901111111")
    r = await client.post("/v1/goals", headers={**s.headers, **idem()}, json={
        "name": "x", "target": 100_000, "saved": 999_999, "user_id": str(uuid.uuid4())})
    assert r.status_code == 422
    assert set(r.json()["fields"]) == {"saved", "user_id"}
    r = await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "type": "expense", "amount": 1, "category_id": "food", "user_id": str(uuid.uuid4())})
    assert r.status_code == 422


async def test_amount_validation(client, container):
    s = await login(client, container, "+998901111111")
    for bad in (0, -5, 10**12 + 1, 1.5, "100"):
        r = await client.post("/v1/transactions", json={
            "type": "expense", "amount": bad, "category_id": "food"},
            headers={**s.headers, **idem()})
        assert r.status_code == 422, bad
    r = await client.post("/v1/goals", json={"name": "x" * 65, "target": 100_000},
                          headers={**s.headers, **idem()})
    assert r.status_code == 422


async def test_export_csv_formula_injection_and_one_time_link(client, container):
    s = await login(client, container, "+998901111111")
    await expense(client, s, 1000, "food", title="=cmd|'/C calc'!A0", note="@SUM(A1)")
    r = await client.post("/v1/exports", headers=s.headers, json={
        "period": "monthly", "include": ["expense", "income"], "format": "csv"})
    assert r.status_code == 202
    assert r.json()["status"] == "pending"
    status = (await client.get(f"/v1/exports/{r.json()['id']}", headers=s.headers)).json()
    assert status["status"] == "ready"
    url = status["download_url"]

    first = await client.get(url)
    assert first.status_code == 200
    assert first.headers["content-disposition"].endswith('.csv"')
    text = first.content.decode("utf-8-sig")
    assert "'=cmd" in text
    assert "'@SUM(A1)" in text
    assert "\n=cmd" not in text and ",=cmd" not in text

    assert (await client.get(url)).status_code == 404  # bir martalik


async def test_delete_account_requires_otp_and_removes_data(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    r = await client.request("DELETE", "/v1/me", headers=s.headers, json={"code": "000000"})
    assert r.status_code == 400  # kod so'ralmagan
    container.kv.time_offset += 61
    assert (await client.post("/v1/me/delete-code", headers=s.headers)).status_code == 200
    r = await client.request("DELETE", "/v1/me", headers=s.headers,
                             json={"code": last_code(container)})
    assert r.status_code == 204
    assert (await client.get("/v1/goals", headers=s.headers)).status_code == 401

    container.kv.time_offset += 61
    again = await login(client, container, "+998901111111")
    assert (await client.get(f"/v1/goals/{goal['id']}", headers=again.headers)).status_code == 404
