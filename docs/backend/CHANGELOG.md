# Finora Backend — CHANGELOG

Backendga oid barcha ishlar shu yerda **teskari xronologik tartibda** yoziladi (eng yangisi tepada).
Har bir yozuvda: sana, nima qilindi, nima uchun, o'zgargan fayllar, muhim qarorlar va ularning sababi.
Katta ishlar uchun batafsil hujjat alohida fayl sifatida shu papkaga yoziladi va shu yerdan havola beriladi.

---

## 2026-09-28 — Xavfsizlik TZ bo'yicha davom: cheklar, AI, eslatmalar, migratsiyalar, CI

Batafsil: [2026-09-28-xavfsizlik-tz-davomi.md](./2026-09-28-xavfsizlik-tz-davomi.md)

**Nima qilindi va nega**

- **Qizil test to'plami tuzatildi** (38 tadan 20 tasi yiqilardi). Sabab: SQLAlchemy 2.1
  `relationship()`siz FK tartibini kafolatlamaydi, `devices` `users`dan oldin INSERT qilinardi.
  Ota qator yaratadigan repository'larga aniq `flush()` qo'shildi. Yana 3 ta test 60 s resend limitiga
  tushardi. Bunda xato kodda emas, test helper'da edi. ruff 16 → 0, mypy 54 → 0.
- **Cheklar** (`/v1/receipts/*`, TZ 4, 6): magic bytes, ClamAV (fail-closed), Pillow bilan qayta
  kodlash (EXIF/GPS yo'q, decompression bomb himoyasi), yopiq ombor, 5 daqiqalik HMAC imzolangan URL,
  30/soat, idempotency. 10 MB limiti faqat `/receipts/scan` yo'liga qo'llanadi.
- **Eslatmalar** (`/v1/reminders`): qabul mezonidagi IDOR ro'yxatida bor edi, lekin modul yo'q edi.
- **AI insights** (`/v1/ai/ask`, TZ 8): faqat jamlangan summalar, savoldan PII tozalanadi, javob
  oddiy matn, 20/soat va 100/kun.
- **Alembic** migratsiyalari (owner roli bilan) + `deploy/db/roles.sql` (ilova roli DDL qila olmaydi)
  + `post_migrate.sql` (audit_log: faqat INSERT, UPDATE taqiqlangan, 1 yildan yangi yozuvni DELETE
  qilib bo'lmaydi).
- **Tozalash vazifasi** `python -m app.jobs purge`: eksportlar 24 soat, idempotency kalitlari 24 soat.
- **CI** (`.github/workflows/backend.yml`): ruff/bandit (SAST), pip-audit (SCA), gitleaks (secret-scan),
  Trivy (konteyner). **Dockerfile** (non-root), **.env.example**, `/.well-known/security.txt`.

**Muhim qarorlar**

- *Tashqi LLM ulanmadi.* TZ 8 bo'yicha provayder shartnomasida "o'qitishda ishlatmaslik" sharti
  MUST, bu huquqiy qaror. Hozircha port + lokal qoidaviy model ishlatiladi.
- *Rasmni qayta kodlash, EXIF segmentlarini kesish emas:* barcha metadata va polyglot payload'lar
  birdaniga yo'qoladi, har bir format uchun alohida parser kerak bo'lmaydi.
- *`cryptography` platforma bo'yicha bo'lindi:* 48.0.1 da 3 ta ma'lum zaiflik bor. Linux'da (CI/prod)
  `>=50`, faqat Intel Mac dev'da `<49` qoldi, chunki u yerda 49+ uchun wheel yo'q.
- *Imzolangan URL uchun alohida `UrlSigner` porti:* prod'da S3 presigned URL bilan almashtiriladi.

**O'zgargan / yangi fayllar**

- Tuzatishlar: `app/infrastructure/db/{models,uow,base}.py`, `app/infrastructure/db/repositories/*`,
  `app/presentation/api/{deps,v1/auth}.py`, `app/presentation/middleware/security.py`, `tests/conftest.py`
- Yangi: `app/{domain,application}/{receipts,reminders}/`, `app/application/insights/`,
  `app/infrastructure/{files,ai}/`, `app/infrastructure/security/url_signer.py`,
  `app/presentation/api/v1/{receipts,reminders,ai}.py`, `app/presentation/schemas/{receipts,reminders,insights}.py`,
  `app/jobs.py`, `migrations/`, `alembic.ini`, `deploy/db/{roles,post_migrate}.sql`, `Dockerfile`,
  `.dockerignore`, `.env.example`, `../.github/workflows/backend.yml`
- Konfiguratsiya: `app/core/config.py`, `app/container.py`, `app/main.py`, `pyproject.toml`, `uv.lock`
- Testlar: `tests/integration/{test_receipts,test_reminders_ai,test_jobs}.py` (38 → 56, hammasi o'tadi)

**Tekshirilmagan / ochiq:** `roles.sql` real Postgres'da ishga tushirilmagan (lokal Postgres yo'q).
SMS, push, S3 va LLM adapterlari hali yo'q. Batafsil hujjatning 11-bo'limiga qarang.

---

## 2026-09-28 — Backend skeleti (`ed86213`)

FastAPI + Clean Architecture skeleti: OTP, tokenlar/sessiyalar/qurilmalar, goals, transactions,
exports, akkauntni o'chirish, xavfsizlik middleware, log maskalash, audit log. (Yozuv keyinroq,
commit tarixi asosida tiklandi.)
