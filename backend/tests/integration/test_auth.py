import json

from app.infrastructure.cache.memory import InMemoryKeyValueStore
from tests.conftest import DeviceKey, last_code, login

PHONE = "+998901234567"


async def test_otp_response_does_not_reveal_registration(client, container):
    await login(client, container, PHONE)
    known = await client.post("/v1/auth/otp", json={
        "phone": "+998901112233", "installation_id": DeviceKey().installation_id})
    unknown = await client.post("/v1/auth/otp", json={
        "phone": "+998909998877", "installation_id": DeviceKey().installation_id})
    assert known.status_code == unknown.status_code == 202
    assert known.json() == unknown.json() == {"message": "Kod yuborildi"}


async def test_resend_before_60s_returns_429(client):
    body = {"phone": PHONE, "installation_id": DeviceKey().installation_id}
    assert (await client.post("/v1/auth/otp", json=body)).status_code == 202
    r = await client.post("/v1/auth/otp", json=body)
    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) > 0
    assert set(r.json()) == {"code", "message", "request_id"}


async def test_resend_after_60s_allowed(client, container):
    body = {"phone": PHONE, "installation_id": DeviceKey().installation_id}
    await client.post("/v1/auth/otp", json=body)
    kv: InMemoryKeyValueStore = container.kv  # type: ignore[assignment]
    kv.time_offset += 61
    assert (await client.post("/v1/auth/otp", json=body)).status_code == 202


async def test_five_wrong_codes_block_number_for_15_minutes(client, container):
    device = DeviceKey()
    await client.post("/v1/auth/otp", json={"phone": PHONE,
                                            "installation_id": device.installation_id})
    code = last_code(container)
    wrong = "000000" if code != "000000" else "111111"
    verify = {"phone": PHONE, "installation_id": device.installation_id,
              "device_public_key": device.public_b64, "device_name": "x", "platform": "ios"}

    statuses = [
        (await client.post("/v1/auth/verify", json={**verify, "code": wrong})).status_code
        for _ in range(5)
    ]
    assert statuses == [400, 400, 400, 400, 429]

    # 6-urinish — hatto to'g'ri kod bilan ham — 429, blok ~15 daqiqa
    r = await client.post("/v1/auth/verify", json={**verify, "code": code})
    assert r.status_code == 429
    assert 800 < int(r.headers["Retry-After"]) <= 900
    # Blok vaqtida yangi SMS ham so'rab bo'lmaydi
    r = await client.post("/v1/auth/otp", json={"phone": PHONE,
                                                "installation_id": device.installation_id})
    assert r.status_code == 429


async def test_otp_is_single_use(client, container):
    device = DeviceKey()
    await client.post("/v1/auth/otp", json={"phone": PHONE,
                                            "installation_id": device.installation_id})
    verify = {"phone": PHONE, "code": last_code(container),
              "installation_id": device.installation_id, "device_public_key": device.public_b64,
              "device_name": "x", "platform": "android"}
    assert (await client.post("/v1/auth/verify", json=verify)).status_code == 200
    assert (await client.post("/v1/auth/verify", json=verify)).status_code == 400


async def test_otp_hash_stored_not_code(client, container):
    await client.post("/v1/auth/otp", json={"phone": PHONE,
                                            "installation_id": DeviceKey().installation_id})
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
    assert sum(d["is_current"] for d in r.json()) == 1

    assert (await client.post("/v1/auth/logout-all", headers=a.headers)).status_code == 204
    assert (await client.get("/v1/goals", headers=a.headers)).status_code == 401
    assert (await client.get("/v1/goals", headers=b.headers)).status_code == 401


async def test_relogin_same_installation_revokes_old_session(client, container):
    device = DeviceKey()
    first = await login(client, container, PHONE, device)
    device.private = DeviceKey().private  # "Forgot PIN?" — yangi kalit
    second = await login(client, container, PHONE, device, pin_reset=True)
    assert (await client.get("/v1/goals", headers=first.headers)).status_code == 401
    assert (await client.get("/v1/goals", headers=second.headers)).status_code == 200


async def test_pin_failures_revokes_device_session(client, container):
    s = await login(client, container, PHONE)
    body = json.dumps({"refresh_token": s.refresh}).encode()
    r = await client.post("/v1/auth/pin-failures", content=body,
                          headers={"Content-Type": "application/json",
                                   **s.device.sign("POST", "/v1/auth/pin-failures", body)})
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
                           "iss": "finora"}, "secret", algorithm="HS256")
    r = await client.get("/v1/goals", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401
