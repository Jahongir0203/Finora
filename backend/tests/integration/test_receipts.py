import io

from PIL import Image

from tests.conftest import idem, login

PHONE_A = "+998901000001"
PHONE_B = "+998901000002"
GPS_TAG = 0x8825


def _jpeg_with_gps() -> bytes:
    img = Image.new("RGB", (64, 48), (200, 10, 10))
    exif = Image.Exif()
    exif[0x010F] = "SecretCam"  # Make
    exif[GPS_TAG] = {1: "N", 2: (41.0, 18.0, 0.0), 3: "E", 4: (69.0, 16.0, 0.0)}
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buf, format="PNG")
    return buf.getvalue()


async def _upload(client, s, data: bytes, **headers: str):
    return await client.post("/v1/receipts/scan", content=data,
                             headers={**s.headers, **idem(), "Content-Type": "image/jpeg",
                                      **headers})


async def test_upload_strips_exif_and_gps(client, container):
    s = await login(client, container, PHONE_A)
    original = _jpeg_with_gps()
    assert Image.open(io.BytesIO(original)).getexif().get(GPS_TAG) is not None

    r = await _upload(client, s, original)
    assert r.status_code == 201, r.text
    receipt = r.json()
    assert receipt["content_type"] == "image/jpeg"

    url = (await client.post(f"/v1/receipts/{receipt['id']}/url", headers=s.headers)).json()["url"]
    img = await client.get(url)
    assert img.status_code == 200
    stored = Image.open(io.BytesIO(img.content))
    assert len(stored.getexif()) == 0
    assert b"SecretCam" not in img.content


async def test_png_accepted_and_converted(client, container):
    s = await login(client, container, PHONE_A)
    r = await _upload(client, s, _png(), **{"Content-Type": "image/png"})
    assert r.status_code == 201
    assert r.json()["content_type"] == "image/jpeg"


async def test_magic_bytes_checked_not_content_type(client, container):
    s = await login(client, container, PHONE_A)
    r = await _upload(client, s, b"<?php system($_GET['c']); ?>" + b"\0" * 100)
    assert r.status_code == 415
    # JPEG sarlavhasi bor, lekin rasm emas (polyglot/buzilgan) — rad etiladi
    r = await _upload(client, s, b"\xff\xd8\xff\xe0" + b"garbage" * 50)
    assert r.status_code == 422
    assert r.json()["code"] == "file_rejected"


async def test_receipt_over_10mb_rejected_and_1mb_elsewhere(client, container):
    s = await login(client, container, PHONE_A)
    big = b"\xff\xd8\xff" + b"0" * (10 * 1024 * 1024)
    assert (await _upload(client, s, big)).status_code == 413


async def test_antivirus_rejects_infected_file(client, container):
    class Infected:
        async def is_clean(self, data: bytes) -> bool:
            return False

    container.scanner = Infected()
    s = await login(client, container, PHONE_A)
    r = await _upload(client, s, _png())
    assert r.status_code == 422
    assert (await client.get("/v1/receipts", headers=s.headers)).json() == []


async def test_receipt_idor_and_signed_url(client, container):
    a = await login(client, container, PHONE_A)
    b = await login(client, container, PHONE_B)
    rid = (await _upload(client, a, _png())).json()["id"]

    assert (await client.get(f"/v1/receipts/{rid}", headers=b.headers)).status_code == 404
    assert (await client.post(f"/v1/receipts/{rid}/url", headers=b.headers)).status_code == 404
    assert (await client.delete(f"/v1/receipts/{rid}", headers=b.headers)).status_code == 404

    url = (await client.post(f"/v1/receipts/{rid}/url", headers=a.headers)).json()["url"]
    assert (await client.get(url)).status_code == 200
    # Imzosiz yoki buzilgan imzo — 404
    base = url.split("?")[0]
    assert (await client.get(base)).status_code == 422
    assert (await client.get(url[:-2] + "xx")).status_code == 404
    # Muddatni uzaytirishga urinish — imzo mos kelmaydi
    tampered = url.replace("exp=", "exp=9")
    assert (await client.get(tampered)).status_code == 404


async def test_signed_url_expires_after_5_minutes(client, container):
    from datetime import timedelta

    s = await login(client, container, PHONE_A)
    rid = (await _upload(client, s, _png())).json()["id"]
    url = (await client.post(f"/v1/receipts/{rid}/url", headers=s.headers)).json()["url"]

    real_now = container.clock.now

    class Later:
        def now(self):
            return real_now() + timedelta(seconds=301)

    container.clock = Later()
    assert (await client.get(url)).status_code == 404


async def test_receipt_upload_idempotent(client, container):
    s = await login(client, container, PHONE_A)
    key = idem()
    data = _png()
    r1 = await _upload(client, s, data, **key)
    r2 = await _upload(client, s, data, **key)
    assert r1.json()["id"] == r2.json()["id"]
    assert len((await client.get("/v1/receipts", headers=s.headers)).json()) == 1


async def test_receipt_rate_limit_30_per_hour(client, container):
    container.settings.receipts_per_hour = 2
    s = await login(client, container, PHONE_A)
    assert (await _upload(client, s, _png())).status_code == 201
    assert (await _upload(client, s, _png())).status_code == 201
    r = await _upload(client, s, _png())
    assert r.status_code == 429
    assert "Retry-After" in r.headers


async def test_delete_account_removes_receipt_files(client, container, settings):
    from pathlib import Path

    s = await login(client, container, PHONE_A)
    await _upload(client, s, _png())
    files = list(Path(settings.storage_dir).rglob("*.jpg"))
    assert files
    assert (await client.delete("/v1/me", headers=s.headers)).status_code == 204
    assert not any(f.exists() for f in files)


async def test_heic_accepted_and_converted(client, container):
    import pillow_heif

    buf = io.BytesIO()
    pillow_heif.from_pillow(Image.new("RGB", (32, 32), (0, 128, 0))).save(buf, quality=50)
    s = await login(client, container, PHONE_A)
    r = await _upload(client, s, buf.getvalue(), **{"Content-Type": "image/heic"})
    assert r.status_code == 201, r.text
    assert r.json()["content_type"] == "image/jpeg"
