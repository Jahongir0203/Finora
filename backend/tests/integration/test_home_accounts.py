"""Home (BE-301), hisoblar (BE-1401..1404), boshlang'ich balans (BE-204), profil (BE-1301..)."""

from tests.conftest import expense, idem, income, login

PHONE = "+998906660001"


async def test_home_for_new_user_is_empty(client, container):
    s = await login(client, container, PHONE)
    r = await client.get("/v1/home", headers={**s.headers, "X-Timezone": "Asia/Tashkent"})
    assert r.status_code == 200, r.text
    home = r.json()
    # *_display maydonlari asosiy valyuta UZS bo'lganda null
    assert home["balance"] == {"total": 0, "currency": "UZS", "need_balance": True,
                               "total_display": None, "display_currency": None}
    assert (home["month"]["income"], home["month"]["expenses"]) == (0, 0)
    assert home["unread_notifications"] == 0
    assert home["get_started"] == {"balance": False, "transaction": False, "goal": False,
                                   "reminder": False}
    assert home["ai_teaser"] is None and home["budget_summary"] is None
    assert home["upcoming_payments"] == [] and home["recent_transactions"] == []


async def test_starting_balance_and_home_totals(client, container):
    s = await login(client, container, PHONE)
    r = await client.post("/v1/onboarding/balance", headers=s.headers,
                          json={"amount": 1_000_000, "location": "both"})
    assert r.status_code == 200, r.text
    accounts = r.json()["accounts"]
    assert [(a["type"], a["opening_balance"]) for a in accounts] == [("cash", 1_000_000),
                                                                    ("card", 0)]
    # Qayta chaqirilsa yangilanadi, dublikat yo'q
    await client.post("/v1/onboarding/balance", headers=s.headers,
                      json={"amount": 2_000_000, "location": "cash"})
    listing = (await client.get("/v1/accounts", headers=s.headers)).json()
    assert listing["count"] == 2 and listing["total"] == 2_000_000

    await income(client, s, 500_000)
    await expense(client, s, 120_000, "food", title="Evos cafe")
    goal = (await client.post("/v1/goals", headers={**s.headers, **idem()},
                              json={"name": "Trip", "target": 1_000_000})).json()
    await client.post(f"/v1/goals/{goal['id']}/deposits", headers={**s.headers, **idem()},
                      json={"amount": 300_000})
    await client.patch("/v1/categories/food", headers=s.headers,
                       json={"monthly_limit": 400_000})
    await client.post("/v1/reminders", headers={**s.headers, **idem()}, json={
        "title": "Internet", "category_id": "bills", "amount": 99_000,
        "due_date": container.clock.now().date().isoformat(), "repeat": "monthly"})

    home = (await client.get("/v1/home", headers=s.headers)).json()
    # 2 000 000 + 500 000 - 120 000 - 300 000 (goal deposit)
    assert home["balance"]["total"] == 2_080_000
    assert home["balance"]["need_balance"] is False
    assert (home["month"]["income"], home["month"]["expenses"]) == (500_000, 120_000)
    assert home["get_started"] == {"balance": True, "transaction": True, "goal": True,
                                   "reminder": True}
    assert home["budget_summary"]["limit"] == 400_000
    assert home["budget_summary"]["spent"] == 120_000
    assert [p["title"] for p in home["upcoming_payments"]] == ["Internet"]
    assert len(home["recent_transactions"]) == 2
    assert home["unread_notifications"] == 1  # goal 25% milestone


async def test_created_transaction_returns_new_balance(client, container):
    s = await login(client, container, PHONE)
    await client.post("/v1/onboarding/balance", headers=s.headers,
                      json={"amount": 100_000, "location": "cash"})
    r = await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "type": "expense", "amount": 30_000, "category_id": "transport"})
    assert r.json()["balance"] == {"total": 70_000}


async def test_accounts_crud_card_fields_and_freeze(client, container):
    s = await login(client, container, PHONE)
    card = {"type": "card", "bank_name": "Kapitalbank", "network": "UZCARD", "last4": "4821",
            "expiry": "08/29", "color": "#064E3B", "opening_balance": 14_250_000,
            "monthly_limit": 10_000_000}
    r = await client.post("/v1/accounts", headers={**s.headers, **idem()}, json=card)
    assert r.status_code == 201, r.text
    acc = r.json()
    assert acc["is_default"] is True and acc["balance"] == 14_250_000
    assert acc["name"] == "Kapitalbank"
    # To'liq karta raqami qabul qilinmaydi
    for bad in ({"last4": "8600123412344821"}, {"card_number": "8600123412344821"},
                {"expiry": "13/29"}):
        r = await client.post("/v1/accounts", headers={**s.headers, **idem()},
                              json={**card, **bad})
        assert r.status_code == 422, bad

    assert (await client.post(f"/v1/accounts/{acc['id']}/freeze",
                              headers=s.headers)).status_code == 204
    r = await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "type": "expense", "amount": 1000, "category_id": "food", "account_id": acc["id"]})
    assert r.status_code == 422 and r.json()["code"] == "account_frozen"
    await client.post(f"/v1/accounts/{acc['id']}/unfreeze", headers=s.headers)
    await expense(client, s, 1000, "food", account_id=acc["id"])

    r = await client.patch(f"/v1/accounts/{acc['id']}", headers=s.headers,
                           json={"name": "Main card"})
    assert r.json()["name"] == "Main card" and r.json()["balance"] == 14_249_000
    # Tranzaksiyasi bor hisob — arxivlanadi (tarix saqlanadi)
    assert (await client.delete(f"/v1/accounts/{acc['id']}", headers=s.headers)).status_code == 204
    assert (await client.get("/v1/accounts", headers=s.headers)).json()["count"] == 0
    txs = (await client.get("/v1/transactions", headers=s.headers)).json()["items"]
    assert len(txs) == 1


async def test_transfer_moves_money_and_is_not_expense(client, container):
    s = await login(client, container, PHONE)
    await client.post("/v1/onboarding/balance", headers=s.headers,
                      json={"amount": 500_000, "location": "both"})
    cash, card = (await client.get("/v1/accounts", headers=s.headers)).json()["items"]
    r = await client.post("/v1/transfers", headers={**s.headers, **idem()}, json={
        "from_account_id": cash["id"], "to_account_id": card["id"], "amount": 200_000})
    assert r.status_code == 201, r.text
    assert r.json()["out"]["direction"] == "out" and r.json()["in"]["direction"] == "in"
    balances = {a["type"]: a["balance"] for a in
                (await client.get("/v1/accounts", headers=s.headers)).json()["items"]}
    assert balances == {"cash": 300_000, "card": 200_000}
    home = (await client.get("/v1/home", headers=s.headers)).json()
    assert home["month"]["expenses"] == 0 and home["balance"]["total"] == 500_000
    stats = (await client.get("/v1/stats?period=month", headers=s.headers)).json()
    assert stats["total_spent"] == 0
    # O'tkazmani o'chirish ikkala tomonni bekor qiladi
    await client.delete(f"/v1/transactions/{r.json()['out']['id']}", headers=s.headers)
    balances = {a["type"]: a["balance"] for a in
                (await client.get("/v1/accounts", headers=s.headers)).json()["items"]}
    assert balances == {"cash": 500_000, "card": 0}


async def test_profile_settings_and_pin_setup(client, container):
    s = await login(client, container, PHONE)
    me = (await client.get("/v1/me", headers=s.headers)).json()
    assert me["phone_masked"] == "+998 90 *** ** 01"
    assert me["language"] == "uz-Latn" and me["currency"] == "UZS" and me["theme"] == "system"
    assert me["counts"] == {"accounts": 0, "categories": 10, "reminders_enabled": 0}
    assert me["device"] == {"auto_lock_minutes": 1, "biometric_enabled": False,
                            "has_pin_setup": False}

    r = await client.patch("/v1/me", headers=s.headers,
                           json={"first_name": "Doston", "last_name": "Karimov"})
    assert r.json()["initials"] == "DK"
    r = await client.patch("/v1/me/settings", headers=s.headers, json={
        "theme": "dark", "currency": "USD", "auto_lock_minutes": 3, "biometric_enabled": True})
    body = r.json()
    assert body["theme"] == "dark" and body["currency"] == "USD"
    assert body["device"]["auto_lock_minutes"] == 3 and body["device"]["biometric_enabled"]
    for bad in ({"auto_lock_minutes": 2}, {"language": "de"}, {"currency": "JPY"},
                {"timezone": "../../etc/passwd"}):
        assert (await client.patch("/v1/me/settings", headers=s.headers,
                                   json=bad)).status_code == 422, bad

    # Qurilma darajasida: boshqa qurilma sozlamasi alohida
    other = await login(client, container, PHONE)
    assert (await client.get("/v1/me", headers=other.headers)).json()["device"][
        "auto_lock_minutes"] == 1
    r = await client.post("/v1/me/pin-setup", headers=s.headers, json={})
    assert r.json()["has_pin_setup"] is True
    r = await client.post("/v1/me/pin-setup", headers=s.headers,
                          json={"device_id": other.device.installation_id})
    assert r.status_code == 404  # boshqa qurilmani belgilab bo'lmaydi


async def test_display_currency_conversion(client, container):
    from datetime import date
    from decimal import Decimal

    from app.domain.currencies.entities import CurrencyRate

    s = await login(client, container, PHONE)
    async with container.uow() as uow:
        await uow.currency_rates.save(CurrencyRate("USD", Decimal("12650.00"), date.today(),
                                                   container.clock.now()))
        await uow.commit()
    await client.patch("/v1/me/settings", headers=s.headers, json={"currency": "USD"})
    tx = await expense(client, s, 126_500, "food")
    listing = (await client.get("/v1/transactions", headers=s.headers)).json()
    assert listing["items"][0]["amount_display"] == "10.00"
    assert listing["items"][0]["display_currency"] == "USD"
    home = (await client.get("/v1/home", headers=s.headers)).json()
    assert home["month"]["expenses_display"] == "10.00"
    del tx
    currencies = (await client.get("/v1/currencies", headers=s.headers)).json()
    usd = next(c for c in currencies if c["code"] == "USD")
    assert usd["rate_to_uzs"] == "12650.0000" and usd["symbol"] == "$"
    assert [c["code"] for c in currencies] == ["UZS", "USD", "EUR", "RUB", "KZT", "GBP", "CNY",
                                               "TRY"]
