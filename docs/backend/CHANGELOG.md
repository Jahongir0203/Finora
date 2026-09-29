# Finora Backend — CHANGELOG

Backendga oid barcha ishlar shu yerda **teskari xronologik tartibda** yoziladi (eng yangisi tepada).
Har bir yozuvda: sana, nima qilindi, nima uchun, o'zgargan fayllar, muhim qarorlar va ularning sababi.
Katta ishlar uchun batafsil hujjat alohida fayl sifatida shu papkaga yoziladi va shu yerdan havola beriladi.

---

## 2026-09-29 — Backend_task.md: hisoblar, kategoriyalar, Home, statistika, eksport, insights, sync

Batafsil (har bir BE-task holati, qarorlar, mobil uchun API o'zgarishlari):
[2026-09-29-backend-tasklar.md](./2026-09-29-backend-tasklar.md) ·
xato kodlari: [ERROR_CODES.md](./ERROR_CODES.md) · API: [openapi.json](./openapi.json)

**Nima qilindi va nega**

- **Hisoblar va kartalar** (BE-1401..1404): `accounts` jadvali, faqat `last4`/`expiry`
  (to'liq raqam qabul qilinmaydi), freeze (`422 account_frozen`), o'tkazmalar (2 bog'langan yozuv),
  boshlang'ich balans `POST /v1/onboarding/balance` (BE-204).
- **Kategoriyalar va byudjetlar** (BE-1501, BE-1001): 10 tizim kategoriyasi (kodda, lokalizatsiya
  bilan) + user kategoriyalari; limit kategoriyada; `GET /v1/budgets` status bilan. Eski `/budgets`
  CRUD olib tashlandi.
- **Tranzaksiyalar v2** (BE-501..505): hisob, `category_id` (turga moslik), `title`, `source`,
  chek, soft delete, PATCH, qidiruv (title/note/kategoriya nomi), cursor pagination, kunlik `groups`.
  Hisob-kitob servisi `Ledger` + Redis kesh.
- **Home** (BE-301), **statistika** (BE-801), **offline sync** (BE-302).
- **Bildirishnomalar** (BE-401..404): 6 tur, `deep_link`, read-all/clear, generatorlar
  (payment_due, budget 75/100%, weekly, goal milestone, security), push outbox + qayta urinish,
  `notifications_enabled`.
- **Eksport** (BE-601/602): preview, asinxron PDF/XLSX/CSV, fayl nomlari, imzolangan bir martalik havola.
- **Cheklar** (BE-701..703): OCR va fiskal QR portlari, QR parser, kategoriya taxmini,
  tasdiqlanmagan cheklarni 24 soatda tozalash.
- **AI** (BE-901..903): 4 qoidaga asoslangan detektor, amallar/dismiss, savol-javob 3 oy
  konteksti bilan, injection filtri, 15 s timeout, suggestions.
- **Goals v2** (BE-1101..1105), **eslatmalar v2** (BE-1201..1203), **profil/sozlamalar/qurilmalar**
  (BE-1301..1304, 201..205), **valyuta** CBU (BE-1602), **FAQ/aloqa/chat sessiyasi** (BE-1701/1702).
- **Lokalizatsiya** (BE-1601): 6 til, xato xabarlari ham. **Xato kodlari lug'ati** (BE-1801).
- **Auth**: `device_id`, `user` obyekti, `attempts_left`, `otp_expired`, `session_expired` /
  `token_expired`, `purpose: pin_reset`, PlayMobile zaxira SMS, attestation porti.
- **Xavfsizlik (oldingi auditdan)**: telefon kalitini almashtirish (`jobs reencrypt-phones`),
  bitta IP'dan ko'p turli raqam alerti, audit retention job'i.
- **Infra**: `/ready`, latency metrikasi, yangi alertlar, `app.seed`, `app.openapi` (+ CI
  tekshiruvi), k6 yuklama skripti, Dockerfile'da PDF shrifti, `roles.sql`da `pg_trgm`.

**Muhim qarorlar** (sabablari batafsil hujjatda): idempotency DB'da (Redis emas); balans
saqlanmaydi — hisoblanadi; goal deposit hisobdan chiqadi; tizim kategoriyasi id — slug;
OCR/Soliq ulanmaganda `503` (422 emas); push navbati `notifications` jadvalining o'zi; tranzaksiyali
hisob o'chirilmaydi — arxivlanadi.

**O'zgargan / yangi fayllar** (asosiylari)

- Yangi domen: `app/domain/{accounts,categories,insights,help,currencies}/`, `app/domain/common/time.py`
- Yangi application: `app/application/{accounts,categories,finance,home,stats,profile,sync,
  currencies,help}/`, `app/application/insights/detectors.py`, `app/application/notifications/
  {triggers,weekly}.py`, `app/application/receipts/parsing.py`, `app/application/exports/report.py`,
  `app/application/common/pagination.py`
- Yangi infra: `app/infrastructure/db/repositories/{accounts,categories,insights,help,currencies}.py`,
  `app/infrastructure/{reports,rates,geo}/`, `app/infrastructure/sms/{playmobile,fallback}.py`
- Yangi API: `app/presentation/api/v1/{home,onboarding,accounts,categories,devices,notifications,
  stats,insights,sync,currencies,help}.py`, `app/presentation/api/factories.py`,
  `app/presentation/middleware/locale.py`, `app/presentation/schemas/{accounts,categories,home,
  profile,stats,exports,misc}.py`
- Yangi: `app/core/i18n.py`, `app/seed.py`, `app/openapi.py`, `loadtest/home_activity_stats.js`,
  `migrations/versions/20260929_b7c1e4d2a9f0_…py`
- Qayta yozilgan: tranzaksiyalar, goals, eslatmalar, bildirishnomalar, eksport, cheklar, insights,
  auth (otp), `app/jobs.py`, `app/infrastructure/db/models.py`, `app/container.py`,
  `app/presentation/errors.py`
- O'chirilgan: `app/{domain,application}/budgets/`, `…/repositories/budgets.py`,
  `…/api/v1/budgets.py`, `…/schemas/budgets.py`
- Deploy/CI: `Dockerfile`, `deploy/db/roles.sql`, `deploy/monitoring/alerts.yml`,
  `.github/workflows/backend.yml`, `.env.example`, `alembic.ini`, `pyproject.toml`
  (fpdf2, openpyxl, tzdata; dev: types-openpyxl), `uv.lock`
- Testlar: 77 → 138 (yangi: `test_home_accounts`, `test_activity_stats`,
  `test_categories_budgets`, `test_goals_insights_exports`, `test_migrations`, `test_i18n`)

**Tekshirilmagan / ochiq:** Postgres'da migratsiya (lokal PG yo'q), OCR va Soliq API
provayderlari, LLM, bank integratsiyasi, live chat provayderi, geo-baza, attestation verifier,
yuklama testi, kk/tr tarjimalarini tekshirish, admin panel. Eslatma: 2026-09-28 xavfsizlik
hujjatidagi holat jadvali eskirgan — joriy holat yangi hujjatda.

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
