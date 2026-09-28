import uuid

from tests.conftest import idem, login


async def _goal(client, s, target=1_000_000):
    r = await client.post("/v1/goals", json={"name": "Mashina", "target_amount": target},
                          headers={**s.headers, **idem()})
    assert r.status_code == 201, r.text
    return r.json()


async def test_idor_returns_404_for_foreign_resources(client, container):
    alice = await login(client, container, "+998901111111")
    bob = await login(client, container, "+998902222222")
    goal = await _goal(client, alice)
    tx = (await client.post("/v1/transactions", headers={**alice.headers, **idem()}, json={
        "kind": "expense", "amount": 5000, "category": "Food",
        "occurred_at": "2026-09-01T10:00:00+05:00"})).json()

    checks = [
        ("GET", f"/v1/goals/{goal['id']}", None),
        ("PATCH", f"/v1/goals/{goal['id']}", {"name": "hack"}),
        ("DELETE", f"/v1/goals/{goal['id']}", None),
        ("POST", f"/v1/goals/{goal['id']}/deposit", {"amount": 1}),
        ("POST", f"/v1/goals/{goal['id']}/withdraw", {"amount": 1}),
        ("GET", f"/v1/transactions/{tx['id']}", None),
        ("DELETE", f"/v1/transactions/{tx['id']}", None),
    ]
    for method, url, body in checks:
        r = await client.request(method, url, json=body, headers={**bob.headers, **idem()})
        assert r.status_code == 404, (method, url, r.status_code)

    # Mavjud bo'lmagan va begona resurs javobi bir xil
    missing = await client.get(f"/v1/goals/{uuid.uuid4()}", headers=bob.headers)
    foreign = await client.get(f"/v1/goals/{goal['id']}", headers=bob.headers)
    assert missing.json()["code"] == foreign.json()["code"] == "not_found"

    devices = (await client.get("/v1/me/devices", headers=alice.headers)).json()
    r = await client.delete(f"/v1/me/devices/{devices[0]['id']}", headers=bob.headers)
    assert r.status_code == 404
    # Alice resurslari buzilmagan
    assert (await client.get(f"/v1/goals/{goal['id']}", headers=alice.headers)).status_code == 200


async def test_ids_are_uuid7(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    assert uuid.UUID(goal["id"]).version == 7


async def test_same_idempotency_key_creates_single_deposit(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    headers = {**s.headers, **idem()}
    r1 = await client.post(f"/v1/goals/{goal['id']}/deposit", json={"amount": 50_000},
                           headers=headers)
    r2 = await client.post(f"/v1/goals/{goal['id']}/deposit", json={"amount": 50_000},
                           headers=headers)
    assert r1.status_code == r2.status_code == 201
    assert r1.json() == r2.json()
    saved = (await client.get(f"/v1/goals/{goal['id']}", headers=s.headers)).json()["saved"]
    assert saved == 50_000


async def test_idempotency_key_reuse_with_other_body_conflicts(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    headers = {**s.headers, **idem()}
    await client.post(f"/v1/goals/{goal['id']}/deposit", json={"amount": 1}, headers=headers)
    r = await client.post(f"/v1/goals/{goal['id']}/deposit", json={"amount": 2}, headers=headers)
    assert r.status_code == 409


async def test_idempotency_key_required(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    r = await client.post(f"/v1/goals/{goal['id']}/deposit", json={"amount": 1},
                          headers=s.headers)
    assert r.status_code == 400
    assert r.json()["code"] == "idempotency_key_required"


async def test_withdraw_more_than_saved_is_422(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    await client.post(f"/v1/goals/{goal['id']}/deposit", json={"amount": 100},
                      headers={**s.headers, **idem()})
    r = await client.post(f"/v1/goals/{goal['id']}/withdraw", json={"amount": 101},
                          headers={**s.headers, **idem()})
    assert r.status_code == 422
    assert r.json()["code"] == "insufficient_funds"
    ok = await client.post(f"/v1/goals/{goal['id']}/withdraw", json={"amount": 100},
                           headers={**s.headers, **idem()})
    assert ok.status_code == 201
    assert ok.json()["saved"] == 0


async def test_mass_assignment_rejected(client, container):
    s = await login(client, container, "+998901111111")
    r = await client.post("/v1/goals", headers={**s.headers, **idem()}, json={
        "name": "x", "target_amount": 10, "saved": 999_999, "user_id": str(uuid.uuid4())})
    assert r.status_code == 422


async def test_amount_validation(client, container):
    s = await login(client, container, "+998901111111")
    for bad in (0, -5, 10**12 + 1, 1.5, "100"):
        r = await client.post("/v1/goals", json={"name": "x", "target_amount": bad},
                              headers={**s.headers, **idem()})
        assert r.status_code == 422, bad
    r = await client.post("/v1/goals", json={"name": "x" * 65, "target_amount": 1},
                          headers={**s.headers, **idem()})
    assert r.status_code == 422


async def test_export_csv_formula_injection_and_one_time_link(client, container):
    s = await login(client, container, "+998901111111")
    await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "kind": "expense", "amount": 1000, "category": "=cmd|'/C calc'!A0",
        "occurred_at": "2026-09-01T10:00:00+05:00", "note": "@SUM(A1)"})
    r = await client.post("/v1/exports", json={}, headers=s.headers)
    assert r.status_code == 201
    url = r.json()["download_url"]

    first = await client.get(url)
    assert first.status_code == 200
    text = first.content.decode("utf-8-sig")
    assert "'=cmd" in text
    assert "'@SUM(A1)" in text
    assert "\n=cmd" not in text and ",=cmd" not in text

    assert (await client.get(url)).status_code == 404  # bir martalik


async def test_delete_account_removes_data(client, container):
    s = await login(client, container, "+998901111111")
    goal = await _goal(client, s)
    assert (await client.delete("/v1/me", headers=s.headers)).status_code == 204
    assert (await client.get("/v1/goals", headers=s.headers)).status_code == 401

    again = await login(client, container, "+998901111111")
    assert (await client.get(f"/v1/goals/{goal['id']}", headers=again.headers)).status_code == 404
