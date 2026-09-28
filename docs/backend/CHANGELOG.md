# Finora Backend — CHANGELOG

Backendga oid barcha ishlar shu yerda **teskari xronologik tartibda** yoziladi (eng yangisi tepada).
Har bir yozuvda: sana, nima qilindi, nima uchun, o'zgargan fayllar, muhim qarorlar va ularning sababi.
Katta ishlar uchun batafsil hujjat alohida fayl sifatida shu papkaga yoziladi va shu yerdan havola beriladi.

---

## 2026-09-28 — Eskiz SMS, push + in-app bildirishnomalar, S3, monitoring, byudjet

Batafsil: [2026-09-28-integratsiyalar-va-monitoring.md](./2026-09-28-integratsiyalar-va-monitoring.md)

**Nima qilindi va nega**

- **Eskiz.uz SMS adapteri.** Prod'da `console` SMS taqiqlangan edi, lekin real adapter yo'q edi.
  Token keshlanadi, 401'da qayta login qilinadi. Xatolar 503 bo'lib qaytadi, OTP va SMS matni loglanmaydi.
- **Push (FCM HTTP v1, APNs) + ilova ichidagi bildirishnomalar.** TZ 2: yangi kirish va refresh
  reuse haqida push va in-app bildirishnoma MUST, oldin faqat log yozilardi. Yangi endpointlar:
  `PUT/DELETE /v1/me/push-token`, `GET /v1/me/notifications`, `POST …/{id}/read`.
- **S3-mos yopiq ombor.** SSE-KMS/AES256, presigned GET URL (5 daq, SigV4), O'zbekistondagi provayder uchun `endpoint_url`.
- **Prometheus metrikalar + `deploy/monitoring/alerts.yml`.** TZ 9: OTP xatolari keskin oshishi,
  refresh reuse va IP flood uchun alertlar. `/metrics` Bearer token bilan himoyalangan.
- **Byudjetlar** (`/v1/budgets`). `spent` serverda, Toshkent vaqti bo'yicha oy chegarasi bilan hisoblanadi.
- Prod guard'lar: prod'da real SMS, push provayderi va S3 bucket majburiy.

**Muhim qarorlar**

- *Push matni umumiy, qurilma nomi faqat in-app'da:* push qulflangan ekranda ko'rinadi.
- *Push token bitta qurilma yozuvida:* telefonda boshqa akkauntga kirilsa, token eski akkauntdan
  olinadi. Aks holda bildirishnoma begona odamga borardi.
- *Push xatosi login'ni yiqitmaydi* (5 s timeout). *SMS xatosi resend limitini qaytarmaydi*, aks
  holda bu limitni aylanib o'tish yo'li bo'lardi.
- *Metrikalar log handler orqali sanaladi*, label'lar oq ro'yxatdan olinadi: PII yo'q, loglar bilan metrikalar ajralib qolmaydi.
- *Oy chegarasi qat'iy UTC+5 bilan:* O'zbekistonda yozgi vaqt yo'q, `tzdata`ga bog'liqlik kerak emas.
- `LogNotifier` o'chirildi (endi ishlatilmaydi).

**O'zgargan / yangi fayllar**

- Yangi: `app/infrastructure/sms/eskiz.py`, `app/infrastructure/push/{fcm,apns,router}.py`,
  `app/infrastructure/storage/s3.py`, `app/application/notifications/{notifier,use_cases}.py`,
  `app/domain/notifications/`, `app/{domain,application}/budgets/`, `app/core/metrics.py`,
  `app/infrastructure/db/repositories/{notifications,budgets}.py`,
  `app/presentation/api/v1/budgets.py`, `app/presentation/schemas/{notifications,budgets}.py`,
  `deploy/monitoring/alerts.yml`, `migrations/versions/20260928_5a24b90a75ad_…py`
- O'zgargan: `app/container.py`, `app/core/{config,logging}.py`, `app/main.py`, `app/jobs.py`,
  `app/application/common/{interfaces,rate_limit,uow}.py`, `app/application/receipts/use_cases.py`,
  `app/infrastructure/db/{models,uow}.py`, `app/infrastructure/storage/local.py`,
  `app/presentation/api/v1/{me,receipts}.py`, `app/presentation/middleware/{security,request_id}.py`,
  `app/presentation/errors.py`, `app/domain/common/errors.py`, `.env.example`, `pyproject.toml`, `uv.lock`
- O'chirilgan: `app/infrastructure/notifications/log_notifier.py`
- Testlar: 56 → 77 (`test_adapters`, `test_notifications`, `test_metrics`, `test_budgets`)

**Bajarilmagan:** LLM (shartnoma kerak), Postgres'da SQL tekshiruvi (lokal Postgres yo'q), branch
protection (GitHub sozlamasi), OCR (provayder va ma'lumot hududi qarori). Sabablari batafsil hujjatda.

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
