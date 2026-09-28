from tests.conftest import idem, login

PHONE_A = "+998902000001"
PHONE_B = "+998902000002"
REMINDER = {"title": "Kommunal to'lov", "due_at": "2026-10-01T09:00:00+05:00",
            "repeat": "monthly", "amount": 350_000}


async def test_reminders_crud_and_idor(client, container):
    a = await login(client, container, PHONE_A)
    b = await login(client, container, PHONE_B)
    r = await client.post("/v1/reminders", json=REMINDER, headers={**a.headers, **idem()})
    assert r.status_code == 201, r.text
    rid = r.json()["id"]

    for method, extra in (("GET", {}), ("PATCH", {"json": {"title": "x"}}), ("DELETE", {})):
        resp = await client.request(method, f"/v1/reminders/{rid}", headers=b.headers, **extra)
        assert resp.status_code == 404, method
    assert (await client.get("/v1/reminders", headers=b.headers)).json() == []

    r = await client.patch(f"/v1/reminders/{rid}", json={"amount": None}, headers=a.headers)
    assert r.status_code == 200
    assert r.json()["amount"] is None and r.json()["title"] == REMINDER["title"]
    assert (await client.delete(f"/v1/reminders/{rid}", headers=a.headers)).status_code == 204


async def test_reminder_mass_assignment_and_validation(client, container):
    a = await login(client, container, PHONE_A)
    h = {**a.headers, **idem()}
    assert (await client.post("/v1/reminders", json={**REMINDER, "user_id": "x"},
                              headers=h)).status_code == 422
    assert (await client.post("/v1/reminders", json={**REMINDER, "title": "x" * 65},
                              headers=h)).status_code == 422
    assert (await client.post("/v1/reminders", json={**REMINDER, "due_at": "2026-10-01T09:00:00"},
                              headers=h)).status_code == 422


async def test_ai_receives_only_aggregates(client, container):
    captured: list[str] = []

    class Spy:
        async def complete(self, system: str, prompt: str) -> str:
            captured.append(system + prompt)
            return "ok"

    container.insights = Spy()
    a = await login(client, container, PHONE_A)
    await client.post("/v1/transactions", headers={**a.headers, **idem()}, json={
        "kind": "expense", "amount": 125_000, "category": "Oziq-ovqat",
        "occurred_at": "2026-09-20T10:00:00+05:00", "note": "Maxfiy izoh 8600123456789012"})
    r = await client.post("/v1/ai/ask", headers=a.headers, json={
        "question": "Karta 8600 1234 5678 9012, tel +998901234567. Qancha tejay olaman?"})
    assert r.status_code == 200, r.text

    sent = captured[0]
    assert "Oziq-ovqat" in sent
    assert "Maxfiy izoh" not in sent  # izohlar yuborilmaydi
    for secret in ("8600", "901234567", PHONE_A[4:]):
        assert secret not in sent


async def test_ai_answer_is_plain_text(client, container):
    class Evil:
        async def complete(self, system: str, prompt: str) -> str:
            return ('<script>alert(1)</script>Tejang! [bosing](https://evil.tld/x) '
                    'javascript:alert(1) <img src=x onerror=1>')

    container.insights = Evil()
    a = await login(client, container, PHONE_A)
    answer = (await client.post("/v1/ai/ask", headers=a.headers,
                                json={"question": "Maslahat"})).json()["answer"]
    assert "<" not in answer and "https://" not in answer and "javascript:" not in answer
    assert "Tejang!" in answer and "bosing" in answer


async def test_ai_rate_limit(client, container):
    container.settings.ai_per_hour = 2
    a = await login(client, container, PHONE_A)
    for _ in range(2):
        assert (await client.post("/v1/ai/ask", headers=a.headers,
                                  json={"question": "?"})).status_code == 200
    r = await client.post("/v1/ai/ask", headers=a.headers, json={"question": "?"})
    assert r.status_code == 429 and "Retry-After" in r.headers


async def test_security_txt(settings, container):
    import httpx

    from app.main import create_app

    settings.security_contact = "mailto:security@example.com"
    app = create_app(settings, container)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                                 base_url="https://api.test") as c:
        r = await c.get("/.well-known/security.txt")
    assert r.status_code == 200
    assert "Contact: mailto:security@example.com" in r.text and "Expires:" in r.text
