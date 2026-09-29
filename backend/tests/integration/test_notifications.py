import json

from app.domain.common.values import PhoneNumber
from tests.conftest import DeviceKey, login

PHONE = "+998904000001"
FCM_A = "fcm-token-device-a-0000000000"
FCM_B = "fcm-token-device-b-0000000000"


async def _register(client, s, token: str, provider: str = "fcm"):
    return await client.post("/v1/devices/current/push-token", headers=s.headers,
                             json={"provider": provider, "token": token, "platform": "ios"})


async def test_new_sign_in_notifies_other_devices(client, container):
    a = await login(client, container, PHONE)
    assert (await _register(client, a, FCM_A)).status_code == 204

    b = await login(client, container, PHONE)  # yangi qurilma
    await _register(client, b, FCM_B)

    sent = container.push.sent
    assert [t for t, _, _ in sent] == [FCM_A]  # yangi qurilmaning o'ziga emas
    _, _, body = sent[0]
    assert "Test phone" not in body  # qulflangan ekranda qurilma nomi ko'rinmaydi

    items = (await client.get("/v1/notifications", headers=a.headers)).json()["items"]
    assert items[0]["type"] == "security" and "Test phone" in items[0]["body"]
    assert items[0]["deep_link"] == "/profile"


async def test_refresh_reuse_notifies_and_invalid_token_cleared(client, container):
    s = await login(client, container, PHONE)
    await _register(client, s, FCM_A)
    body = json.dumps({"refresh_token": s.refresh}).encode()

    def sign():
        return {"Content-Type": "application/json",
                **s.device.sign("POST", "/v1/auth/refresh", body)}

    assert (await client.post("/v1/auth/refresh", content=body, headers=sign())).status_code == 200
    container.push.invalid.add(FCM_A)
    r = await client.post("/v1/auth/refresh", content=body, headers=sign())  # reuse
    assert r.status_code == 401

    assert await _targets(container, PHONE) == []  # 410/UNREGISTERED token bazadan olindi


async def test_notifications_are_private_and_mark_read(client, container):
    a = await login(client, container, PHONE)
    await login(client, container, PHONE, DeviceKey())  # a'ga "yangi kirish" yozuvi
    other = await login(client, container, "+998904000002")
    page = (await client.get("/v1/notifications", headers=a.headers)).json()
    nid = page["items"][0]["id"]
    assert page["unread"] == 1

    assert (await client.get("/v1/notifications", headers=other.headers)).json()["items"] == []
    r = await client.post(f"/v1/notifications/{nid}/read", headers=other.headers)
    assert r.status_code == 404
    r = await client.post(f"/v1/notifications/{nid}/read", headers=a.headers)
    assert r.status_code == 204
    page = (await client.get("/v1/notifications", headers=a.headers)).json()
    assert page["items"][0]["read"] is True and page["unread"] == 0


async def test_delete_one_notification(client, container):
    a = await login(client, container, PHONE)
    await login(client, container, PHONE, DeviceKey())
    other = await login(client, container, "+998904000002")
    nid = (await client.get("/v1/notifications", headers=a.headers)).json()["items"][0]["id"]

    # Begona bildirishnomani o'chirib bo'lmaydi (IDOR).
    r = await client.delete(f"/v1/notifications/{nid}", headers=other.headers)
    assert r.status_code == 404
    r = await client.delete(f"/v1/notifications/{nid}", headers=a.headers)
    assert r.status_code == 204
    page = (await client.get("/v1/notifications", headers=a.headers)).json()
    assert page["items"] == [] and page["unread"] == 0
    r = await client.delete(f"/v1/notifications/{nid}", headers=a.headers)
    assert r.status_code == 404


async def test_push_token_moves_between_accounts_on_same_phone(client, container):
    a = await login(client, container, PHONE)
    await _register(client, a, FCM_A)
    other = await login(client, container, "+998904000002")
    await _register(client, other, FCM_A)  # bir telefon, boshqa akkaunt

    assert await _targets(container, PHONE) == []  # birinchi akkaunt bu telefonga yubormaydi
    assert len(await _targets(container, "+998904000002")) == 1


async def _targets(container, phone: str):
    async with container.uow() as uow:
        user = await uow.users.get_by_phone_index(
            container.hasher.phone_index(PhoneNumber(phone)))
        return await uow.push_tokens.targets(user.id, active_only=False)


async def test_push_token_validation(client, container):
    s = await login(client, container, PHONE)
    assert (await _register(client, s, "short")).status_code == 422
    assert (await _register(client, s, "x" * 20 + "<script>")).status_code == 422
    assert (await _register(client, s, FCM_A, provider="sms")).status_code == 422
    assert (await client.delete("/v1/devices/current/push-token",
                                headers=s.headers)).status_code == 204


async def test_read_all_clear_and_pagination(client, container):
    a = await login(client, container, PHONE)
    for _ in range(3):
        await login(client, container, PHONE, DeviceKey())  # 3 ta "yangi kirish"
    page = (await client.get("/v1/notifications?limit=2", headers=a.headers)).json()
    assert len(page["items"]) == 2 and page["next_cursor"]
    rest = (await client.get(f"/v1/notifications?limit=2&cursor={page['next_cursor']}",
                             headers=a.headers)).json()
    assert len(rest["items"]) == 1 and rest["next_cursor"] is None
    assert {i["id"] for i in page["items"]}.isdisjoint({i["id"] for i in rest["items"]})

    r = await client.post("/v1/notifications/read-all", headers=a.headers)
    assert r.json() == {"count": 3}
    assert (await client.get("/v1/notifications", headers=a.headers)).json()["unread"] == 0
    assert (await client.delete("/v1/notifications", headers=a.headers)).json() == {"count": 3}
    assert (await client.get("/v1/notifications", headers=a.headers)).json()["items"] == []


async def test_disabled_notifications_store_in_app_but_skip_push(client, container):
    a = await login(client, container, PHONE)
    await _register(client, a, FCM_A)
    r = await client.patch("/v1/me/settings", headers=a.headers,
                           json={"notifications_enabled": False})
    assert r.status_code == 200 and r.json()["notifications_enabled"] is False
    goal = (await client.post("/v1/goals", headers={**a.headers, "Idempotency-Key": "g1"},
                              json={"name": "Car", "target": 100_000})).json()
    container.push.sent.clear()
    r = await client.post(f"/v1/goals/{goal['id']}/deposits",
                          headers={**a.headers, "Idempotency-Key": "d1"},
                          json={"amount": 50_000})
    assert r.status_code == 201
    items = (await client.get("/v1/notifications", headers=a.headers)).json()["items"]
    assert [i["type"] for i in items] == ["goal_milestone", "goal_milestone"]  # 25% va 50%
    assert container.push.sent == []  # push yuborilmadi, in-app bor


async def test_failed_push_is_retried_by_job(client, container):
    from app.jobs import run

    a = await login(client, container, PHONE)
    await _register(client, a, FCM_A)
    container.push.fail = True
    await login(client, container, PHONE, DeviceKey())
    assert container.push.sent == []
    container.push.fail = False
    result = await run(container, "push")
    assert result["push_retried"] == 1
    assert [t for t, _, _ in container.push.sent] == [FCM_A]
