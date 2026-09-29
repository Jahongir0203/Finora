import io

from PIL import Image

from tests.conftest import delete_account, expense, idem, login

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
    assert receipt["has_image"] is True
    # OCR natijasi va do'kon nomidan kategoriya taxmini (BE-701)
    assert receipt["merchant"] == "Korzinka Chilonzor" and receipt["total"] == 86_500
    assert receipt["suggested_category_id"] == "groceries"
    assert receipt["items"][0] == {"name": "Non", "quantity": 2.0, "price": 5000}

    url = (await client.post(f"/v1/receipts/{receipt['id']}/url", headers=s.headers)).json()["url"]
    img = await client.get(url)
    assert img.status_code == 200
    assert img.headers["content-type"] == "image/jpeg"
    stored = Image.open(io.BytesIO(img.content))
    assert len(stored.getexif()) == 0
    assert b"SecretCam" not in img.content


async def test_png_accepted_and_converted(client, container):
    s = await login(client, container, PHONE_A)
    r = await _upload(client, s, _png(), **{"Content-Type": "image/png"})
    assert r.status_code == 201
    assert r.json()["has_image"] is True


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
    assert (await client.get("/v1/receipts", headers=s.headers)).json()["items"] == []


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
    assert len((await client.get("/v1/receipts", headers=s.headers)).json()["items"]) == 1


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
    await delete_account(client, container, s)
    assert not any(f.exists() for f in files)


async def test_heic_accepted_and_converted(client, container):
    import pillow_heif

    buf = io.BytesIO()
    pillow_heif.from_pillow(Image.new("RGB", (32, 32), (0, 128, 0))).save(buf, quality=50)
    s = await login(client, container, PHONE_A)
    r = await _upload(client, s, buf.getvalue(), **{"Content-Type": "image/heic"})
    assert r.status_code == 201, r.text
    assert r.json()["has_image"] is True


async def test_unreadable_receipt_is_422_and_not_stored(client, container, settings):
    from pathlib import Path

    container.ocr.result = None
    s = await login(client, container, PHONE_A)
    r = await _upload(client, s, _png())
    assert r.status_code == 422 and r.json()["code"] == "receipt_unreadable"
    assert not list(Path(settings.storage_dir).rglob("*.jpg"))


async def test_no_ocr_provider_is_503(client, container):
    container.ocr = None
    s = await login(client, container, PHONE_A)
    r = await _upload(client, s, _png())
    assert r.status_code == 503 and r.json()["code"] == "ocr_unavailable"


async def test_scanned_receipt_confirmed_by_transaction_and_unconfirmed_purged(client,
                                                                              container):
    from datetime import timedelta

    from app.jobs import purge

    s = await login(client, container, PHONE_A)
    kept = (await _upload(client, s, _png())).json()
    dropped = (await _upload(client, s, _png())).json()
    tx = await expense(client, s, kept["total"], kept["suggested_category_id"],
                       receipt_id=kept["id"], title=kept["merchant"])
    assert tx["source"] == "scan" and tx["receipt_id"] == kept["id"]

    real_now = container.clock.now

    class Later:
        def now(self):
            return real_now() + timedelta(hours=25)

    container.clock = Later()
    assert (await purge(container))["receipts"] == 1
    assert (await client.get(f"/v1/receipts/{kept['id']}", headers=s.headers)).status_code == 200
    assert (await client.get(f"/v1/receipts/{dropped['id']}",
                             headers=s.headers)).status_code == 404


async def test_fiscal_qr(client, container):
    from datetime import datetime

    from app.domain.receipts.entities import ParsedReceipt

    class Soliq:
        async def fetch(self, terminal_id, receipt_number, fiscal_sign, issued_at):
            assert (terminal_id, receipt_number, fiscal_sign) == ("UZ191211502345", "1822",
                                                                  "283920193847")
            return ParsedReceipt(merchant="EVOS", total=64_000, occurred_at=None)

    container.fiscal = Soliq()
    s = await login(client, container, PHONE_A)
    qr = ("https://ofd.soliq.uz/check?t=UZ191211502345&r=1822&c=20260928193011"
          "&s=283920193847")
    r = await client.post("/v1/receipts/qr", headers={**s.headers, **idem()},
                          json={"payload": qr})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["merchant"] == "EVOS" and body["total"] == 64_000
    assert body["suggested_category_id"] == "food" and body["has_image"] is False
    assert datetime.fromisoformat(body["occurred_at"]).hour == 14  # 19:30 Toshkent = 14:30 UTC

    for bad in ("https://example.com/check?t=1&r=2&c=3&s=4", "just text",
                "https://ofd.soliq.uz/check?t=UZ1&r=x"):
        r = await client.post("/v1/receipts/qr", headers={**s.headers, **idem()},
                              json={"payload": bad})
        assert r.status_code == 422 and r.json()["code"] == "qr_not_supported", bad
