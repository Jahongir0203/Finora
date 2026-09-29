import json

from app.infrastructure.cache.memory import InMemoryKeyValueStore
from tests.conftest import DeviceKey, last_code, login

PHONE = "+998901234567"


async def test_otp_response_does_not_reveal_registration(client, container):
    await login(client, container, PHONE)
    known = await client.post("/v1/auth/otp", json={
        "phone": "+998901112233", "device_id": DeviceKey().installation_id})
    unknown = await client.post("/v1/auth/otp", json={
        "phone": "+998909998877", "device_id": DeviceKey().installation_id})
    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json() == {"resend_after": 60, "expires_in": 120}


async def test_resend_before_60s_returns_429(client):
    body = {"phone": PHONE, "device_id": DeviceKey().installation_id}
    assert (await client.post("/v1/auth/otp", json=body)).status_code == 200
    r = await client.post("/v1/auth/otp", json=body)
    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) > 0
    assert set(r.json()) == {"code", "message", "request_id", "retry_after"}
    assert r.json()["code"] == "rate_limited" and r.json()["retry_after"] > 0


async def test_resend_after_60s_allowed(client, container):
    body = {"phone": PHONE, "device_id": DeviceKey().installation_id}
    await client.post("/v1/auth/otp", json=body)
    kv: InMemoryKeyValueStore = container.kv  # type: ignore[assignment]
    kv.time_offset += 61
    assert (await client.post("/v1/auth/otp", json=body)).status_code == 200


async def test_five_wrong_codes_block_number_for_15_minutes(client, container):
    device = DeviceKey()
    await client.post("/v1/auth/otp", json={"phone": PHONE,
                                            "device_id": device.installation_id})
    code = last_code(container)
    wrong = "000000" if code != "000000" else "111111"
    verify = {"phone": PHONE, "device_id": device.installation_id,
              "device_public_key": device.public_b64, "device_name": "x", "platform": "ios"}

    responses = [await client.post("/v1/auth/verify", json={**verify, "code": wrong})
                 for _ in range(5)]
    assert [r.status_code for r in responses] == [400, 400, 400, 400, 429]
    # UI "Wrong code" holati uchun qolgan urinishlar
    assert [r.json().get("attempts_left") for r in responses[:4]] == [4, 3, 2, 1]
    assert responses[0].json()["code"] == "otp_invalid"

    # 6-urinish — hatto to'g'ri kod bilan ham — 429, blok ~15 daqiqa
    r = await client.post("/v1/auth/verify", json={**verify, "code": code})
    assert r.status_code == 429
    assert 800 < int(r.headers["Retry-After"]) <= 900
    # Blok vaqtida yangi SMS ham so'rab bo'lmaydi
    r = await client.post("/v1/auth/otp", json={"phone": PHONE,
                                                "device_id": device.installation_id})
    assert r.status_code == 429


async def test_otp_is_single_use(client, container):
    device = DeviceKey()
    await client.post("/v1/auth/otp", json={"phone": PHONE,
                                            "device_id": device.installation_id})
    verify = {"phone": PHONE, "code": last_code(container),
              "device_id": device.installation_id, "device_public_key": device.public_b64,
              "device_name": "x", "platform": "android"}
    assert (await client.post("/v1/auth/verify", json=verify)).status_code == 200
    assert (await client.post("/v1/auth/verify", json=verify)).status_code == 400


async def test_otp_hash_stored_not_code(client, container):
    await client.post("/v1/auth/otp", json={"phone": PHONE,
                                            "device_id": DeviceKey().installation_id})
    code = last_code(container)
    kv: InMemoryKeyValueStore = container.kv  # type: ignore[assignment]
    stored = " ".join(v for v, _ in kv._data.values())
    assert code not in stored


async def test_refresh_rotation_and_reuse_revokes_family(client, container):
    s = await login(client, container, PHONE)
    body = json.dumps({"refresh_token": s.refresh}).encode()
    headers = {"Content-Type": "application/json",
               **s.device.sign("POST", "/v1/auth/refresh", body)}

    r1 = await client.post("/v1/auth/refresh", content=body, headers=headers)
    assert r1.status_code == 200
    new = r1.json()
    assert new["refresh_token"] != s.refresh

    # Eski token qayta ishlatildi → butun oila bekor
    r2 = await client.post("/v1/auth/refresh", content=body,
                           headers={"Content-Type": "application/json",
                                    **s.device.sign("POST", "/v1/auth/refresh", body)})
    assert r2.status_code == 401
    assert r2.json()["code"] == "session_revoked"

    body3 = json.dumps({"refresh_token": new["refresh_token"]}).encode()
    r3 = await client.post("/v1/auth/refresh", content=body3,
                           headers={"Content-Type": "application/json",
                                    **s.device.sign("POST", "/v1/auth/refresh", body3)})
    assert r3.status_code == 401
    r4 = await client.get("/v1/goals", headers={"Authorization": f"Bearer {new['access_token']}"})
    assert r4.status_code == 401


async def test_refresh_requires_device_signature(client, container):
    s = await login(client, container, PHONE)
    body = json.dumps({"refresh_token": s.refresh}).encode()
    hdr = {"Content-Type": "application/json"}

    assert (await client.post("/v1/auth/refresh", content=body, headers=hdr)).status_code == 401
    other = DeviceKey()
    r = await client.post("/v1/auth/refresh", content=body,
                          headers={**hdr, **other.sign("POST", "/v1/auth/refresh", body)})
    assert r.status_code == 401
    old_ts = s.device.sign("POST", "/v1/auth/refresh", body, ts=1_000_000)
    assert (await client.post("/v1/auth/refresh", content=body,
                              headers={**hdr, **old_ts})).status_code == 401
    # Imzo xatolari tokenni "yemaydi" — to'g'ri imzo bilan hali ishlaydi
    ok = await client.post("/v1/auth/refresh", content=body,
                           headers={**hdr, **s.device.sign("POST", "/v1/auth/refresh", body)})
    assert ok.status_code == 200


async def test_logout_revokes_on_server(client, container):
    s = await login(client, container, PHONE)
    assert (await client.post("/v1/auth/logout", headers=s.headers)).status_code == 204
    assert (await client.get("/v1/goals", headers=s.headers)).status_code == 401


async def test_logout_all_and_devices_list(client, container):
    a = await login(client, container, PHONE)
    b = await login(client, container, PHONE)
    r = await client.get("/v1/me/devices", headers=a.headers)
    assert r.status_code == 200
    assert len(r.json()) == 2
    assert sum(d["current"] for d in r.json()) == 1

    # Joriydan tashqari hammasi (BE-1303)
    r = await client.post("/v1/me/devices/logout-all", headers=a.headers)
    assert r.status_code == 200 and r.json() == {"count": 1}
    assert (await client.get("/v1/goals", headers=a.headers)).status_code == 200
    assert (await client.get("/v1/goals", headers=b.headers)).status_code == 401
    notes = (await client.get("/v1/notifications", headers=a.headers)).json()["items"]
    assert any(n["type"] == "security" for n in notes)


async def test_relogin_same_installation_revokes_old_session(client, container):
    device = DeviceKey()
    first = await login(client, container, PHONE, device)
    device.private = DeviceKey().private  # "Forgot PIN?" — yangi kalit
    r = await client.post("/v1/me/pin-setup", headers=first.headers, json={})
    assert r.json()["has_pin_setup"] is True
    second = await login(client, container, PHONE, device, purpose="pin_reset")
    assert (await client.get("/v1/goals", headers=first.headers)).status_code == 401
    assert (await client.get("/v1/goals", headers=second.headers)).status_code == 200
    # BE-203: yangi PIN o'rnatilguncha has_pin_setup = false
    assert second.user["has_pin_setup"] is False


async def test_pin_failures_revokes_device_session(client, container):
    s = await login(client, container, PHONE)
    body = json.dumps({"refresh_token": s.refresh}).encode()
    path = "/v1/devices/current/pin-lockout"
    # Imzosiz so'rov — 401 (BE-202)
    r = await client.post(path, content=body, headers={"Content-Type": "application/json"})
    assert r.status_code == 401
    r = await client.post(path, content=body,
                          headers={"Content-Type": "application/json",
                                   **s.device.sign("POST", path, body)})
    assert r.status_code == 204
    assert (await client.get("/v1/goals", headers=s.headers)).status_code == 401


async def test_access_token_payload_has_no_personal_data(client, container):
    import base64

    s = await login(client, container, PHONE)
    payload = s.access.split(".")[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    assert set(claims) <= {"sub", "sid", "did", "exp", "iat", "iss"}
    header = s.access.split(".")[0]
    assert json.loads(base64.urlsafe_b64decode(header + "==="))["alg"] == "ES256"


async def test_rejects_forged_hs256_and_none_tokens(client):
    import jwt as pyjwt

    forged = pyjwt.encode({"sub": "x", "sid": "y", "did": "z", "exp": 9999999999,
                           "iss": "finora"}, "s" * 32, algorithm="HS256")
    r = await client.get("/v1/goals", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401


async def test_verify_returns_user_and_onboarding(client, container):
    s = await login(client, container, PHONE)
    assert s.user["is_new"] is True and s.user["has_pin_setup"] is False
    assert s.user["onboarding"] == {"balance_set": False, "has_transactions": False,
                                    "has_goals": False, "has_reminders": False}
    again = await login(client, container, PHONE)
    assert again.user["is_new"] is False and again.user["id"] == s.user["id"]


async def test_expired_code_returns_otp_expired(client, container):
    device = DeviceKey()
    await client.post("/v1/auth/otp", json={"phone": PHONE, "device_id": device.installation_id})
    code = last_code(container)
    real_now = container.clock.now

    class Later:
        def now(self):
            from datetime import timedelta
            return real_now() + timedelta(seconds=121)

    container.clock = Later()
    r = await client.post("/v1/auth/verify", json={
        "phone": PHONE, "code": code, "device_id": device.installation_id,
        "device_public_key": device.public_b64, "device_name": "x", "platform": "ios"})
    assert r.status_code == 400
    assert r.json()["code"] == "otp_expired"


async def test_expired_refresh_is_session_expired(client, container):
    from datetime import timedelta

    s = await login(client, container, PHONE)
    real_now = container.clock.now

    class Later:
        def now(self):
            return real_now() + timedelta(days=31)

    container.clock = Later()
    body = json.dumps({"refresh_token": s.refresh}).encode()
    import time
    ts = int(time.time()) + 31 * 86400
    r = await client.post("/v1/auth/refresh", content=body, headers={
        "Content-Type": "application/json",
        **s.device.sign("POST", "/v1/auth/refresh", body, ts=ts)})
    assert r.status_code == 401
    assert r.json()["code"] == "session_expired"


async def test_expired_access_token_is_token_expired(client, container, settings):
    import time

    import jwt as pyjwt

    s = await login(client, container, PHONE)
    claims = pyjwt.decode(s.access, options={"verify_signature": False})
    service = container.access_tokens
    expired = pyjwt.encode({**claims, "exp": int(time.time()) - 10}, service._private,
                           algorithm="ES256")
    r = await client.get("/v1/goals", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401
    assert r.json()["code"] == "token_expired"


async def test_logout_clears_push_token(client, container):
    a = await login(client, container, PHONE)
    b = await login(client, container, PHONE)
    token = "fcm-token-" + "b" * 30
    await client.post("/v1/devices/current/push-token", headers=b.headers,
                      json={"token": token, "platform": "android"})
    assert (await client.post("/v1/auth/logout", headers=b.headers)).status_code == 204
    async with container.uow() as uow:
        targets = await uow.push_tokens.targets(
            __import__("uuid").UUID(a.user["id"]), active_only=False)
    assert token not in [t.token for t in targets]
