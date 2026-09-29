# 2026-09-29 — Backend_task.md bo'yicha ishlar

Manba: `backend/docs/Backend_task.md` (BE-001 … BE-1903). Bu hujjat — har bir task holati,
muhim qarorlar, mobil uchun API o'zgarishlari va ochiq qolgan ishlar.

Tekshiruv: **138 test** (oldin 77), `ruff`, `mypy --strict`, `bandit`, `alembic upgrade head &&
alembic check`, `python -m app.openapi --check` — hammasi yashil. Postgres'da ishga
tushirilmagan (lokal Postgres yo'q) — SQLite'da testlangan, PG-ga xos qismlar pastda.

---

## 1. Tasklar holati

✅ bajarildi · ⚠️ qisman / tashqi qaror kerak · ❌ bajarilmadi

| Task | Holat | Izoh |
|---|---|---|
| BE-001 Skelet, muhitlar | ⚠️ | `/health`, `/ready` (DB + Redis), seed (`python -m app.seed` — FAQ). Kategoriya/valyuta/til kodda. Staging'ga CI deploy — infratuzilma |
| BE-002 Middleware | ✅ | `422` + `fields[]`, `retry_after`, til middleware. Idempotency — Redis emas, DB'da (quyida qaror) |
| BE-003 CI/CD skanerlar | ✅ / ⚠️ | Oldin qilingan + OpenAPI tekshiruvi. Vault — infratuzilma |
| BE-004 Monitoring | ⚠️ | Latency histogram (route bo'yicha), 5xx, 429 + yangi alertlar. Tracing (OpenTelemetry) — qilinmadi |
| BE-005 Audit log | ✅ | + `jobs audit-retention` (owner roli bilan, 1 yil) |
| BE-101 OTP yuborish | ✅ | `device_id`, javob `{resend_after, expires_in}`, PlayMobile zaxira provayderi |
| BE-102 OTP tasdiqlash | ✅ | `user {id, first_name, is_new, has_pin_setup, onboarding}`, `attempts_left`, `otp_expired` |
| BE-103 Refresh | ✅ | Muddati o'tgan → `401 session_expired`; access muddati → `token_expired` |
| BE-104 Logout | ✅ | + push token o'chiriladi |
| BE-105 Yangi qurilma bildirishnomasi | ⚠️ | Push + in-app `security`. Shahar — `GeoLocator` porti, geo-baza ulanmagan (`city: null`) |
| BE-106 Play Integrity / App Attest | ⚠️ | `attestation_token` qabul qilinadi, `AttestationVerifier` porti va `FINORA_ATTESTATION_REQUIRED`. Real Google/Apple tekshiruvi va SIM-swap — yo'q |
| BE-201 PIN o'rnatildi | ✅ | `POST /v1/me/pin-setup` |
| BE-202 PIN lockout | ✅ | `POST /v1/devices/current/pin-lockout`, imzosiz — 401 |
| BE-203 Forgot PIN | ✅ | `purpose: "pin_reset"` → eski sessiya bekor, `has_pin_setup=false`, audit, `security` |
| BE-204 Starting balance | ✅ | `POST /v1/onboarding/balance`, `opening_balance`, dublikatsiz |
| BE-205 Auto-lock, biometriya | ✅ | `PATCH /v1/me/settings` — qurilma darajasida |
| BE-301 Home | ✅ | `GET /v1/home`. p95 o'lchanmagan (k6 skripti tayyor) |
| BE-302 Offline sync | ✅ | `GET /v1/sync?since=`, soft delete, `client_created_at` |
| BE-401/402 Bildirishnomalar | ✅ | Cursor pagination, `read-all`, `Clear` (soft delete) |
| BE-403 Generatorlar | ⚠️ | payment_due, budget 75/100%, weekly, goal milestone, security ✅. `income` — faqat bank sync'dan, bank yo'q (BE-1405) |
| BE-404 Push navbati | ✅ | Outbox (`push_status`), 3 marta qayta urinish, yaroqsiz token tozalanadi |
| BE-501..505 Tranzaksiyalar | ✅ | Hisob, `category_id`, turga moslik, qidiruv, kunlik `groups`, PATCH, soft delete, hisob-kitob servisi + Redis kesh |
| BE-601/602 Eksport | ✅ | Preview, asinxron job, PDF / XLSX (2 varaq) / CSV, bir martalik imzolangan havola |
| BE-701 Chek OCR | ⚠️ | Quvur tayyor (magic bytes → antivirus → EXIF → OCR → ombor), kategoriya taxmini. **OCR provayderi ulanmagan** → `503 ocr_unavailable` |
| BE-702 Fiskal QR | ⚠️ | QR parser (ofd.soliq.uz) va `FiscalReceiptProvider` porti. Soliq API adapteri yo'q → `503` |
| BE-703 Skanerdan tranzaksiya | ✅ | `receipt_id` bilan chek tasdiqlanadi, tasdiqlanmagani 24 soatda o'chadi |
| BE-801 Statistika | ✅ | Week/Month/Year, foizlar yig'indisi 100, `has_enough_data` |
| BE-901/902 Tavsiyalar | ✅ | 4 detektor, amallar, dismiss. LLM bilan jilolash — shartnomadan keyin |
| BE-903 AI savol-javob | ⚠️ | 3 oy konteksti, 600 belgi, til, injection filtri, 15 s → 503, suggestions. Real LLM yo'q (lokal qoida modeli) |
| BE-1001 Byudjetlar | ✅ | Limit kategoriyada, `GET /v1/budgets?month=` |
| BE-1101..1105 Goals | ✅ | Hisobga bog'langan deposit/withdraw, o'chirishda qaytarish, reja, tarix, milestone, auto-save |
| BE-1201..1203 Eslatmalar | ✅ | `once/weekly/monthly/yearly`, oy oxiri, `pay` |
| BE-1301..1304 Profil | ✅ | O'chirish — SMS kod bilan |
| BE-1401..1404 Hisoblar | ✅ | To'liq karta raqami qabul qilinmaydi, freeze, o'tkazma |
| BE-1405 Bank integratsiyasi | ❌ | Ochiq savol №1 |
| BE-1501 Kategoriyalar | ✅ | 10 tizim + user, ikon/rang ro'yxati, `409`, `reassign_to` |
| BE-1601 Lokalizatsiya | ✅ | 6 til; uz-Cyrl avtomatik. **kk va tr matnlarini ona tili egasi tekshirsin** |
| BE-1602 Valyuta | ✅ | CBU (jonli tekshirildi), kunlik job, `*_display` |
| BE-1701 FAQ | ✅ | Jadval + seed (en/uz/ru). Admin UI yo'q — jadvalni to'g'ridan-to'g'ri |
| BE-1702 Live chat | ⚠️ | `POST /v1/support/session` (HMAC identity). Provayder tanlanmagan |
| BE-1801/1802 Xato kodlari, empty | ✅ | [ERROR_CODES.md](./ERROR_CODES.md), `onboarding` holati |
| BE-1901 OpenAPI | ✅ | [openapi.json](./openapi.json), CI eskirganini tekshiradi |
| BE-1902 Testlar | ⚠️ | 138 test, 02-backend qabul mezonlari. Yuklama testi yozildi (`backend/loadtest/`), ishga tushirilmagan |
| BE-1903 Admin panel | ❌ | P2, admin autentifikatsiya modeli kerak |

Qo'shimcha (oldingi audit): telefon shifrlash kalitini almashtirish (`KEY_VERSION`,
`KEYS_PREVIOUS`, `jobs reencrypt-phones`), bitta IP'dan ko'p **turli** raqam alerti.

---

## 2. Muhim qarorlar va sabablari

- **Idempotency DB'da, Redis'da emas.** Kalit va javob yozuv bilan *bitta DB tranzaksiyasida*
  saqlanadi. Redis'da bo'lsa, "yozuv bor, kalit yo'q" (yoki aksincha) holati mumkin — pulda xavfli.
- **Balans saqlanmaydi, hisoblanadi.** `opening_balance + kirim - chiqim ± o'tkazma - goal deposit
  + goal withdraw`. Bitta formula `Ledger`da; Redis kesh user versiyasi bilan invalidatsiya
  qilinadi. Commit'dan oldingi hisob-kitob keshga yozilmaydi (`fresh=True`).
- **Goal deposit hisobdan chiqadi.** Spec: "asosiy hisob balansi mos ravishda o'zgaradi". Goal
  o'chirilganda qoldiq `close` yozuvi bilan standart hisobga qaytadi, goal soft delete.
- **Tizim kategoriyalari kodda, id — slug** (`groceries`). Spec misolidagi `category_id:
  "groceries"` bilan mos; har bir userga 10 qator ko'chirish shart emas. Limit va nom override
  alohida `category_prefs`da.
- **O'tkazma — ikki bog'langan yozuv** (`out`/`in`, `transfer_peer_id`). O'chirish/tahrirlash
  ikkalasiga ta'sir qiladi; statistikada xarajat emas.
- **Til:** `Accept-Language` bo'lsa shu, bo'lmasa `user.language`. Fon vazifalari (push) doim
  `user.language`da. uz-Cyrl qoidaga ko'ra lotindan o'giriladi (bitta manba).
- **Vaqt:** bazada UTC, javoblarda UTC. Kun/hafta/oy chegaralari `X-Timezone` bo'yicha; zona
  userda saqlanadi (fon vazifalari 09:00/10:00 mahalliy vaqtda).
- **OCR va Soliq API yo'q bo'lsa 503**, "o'qib bo'lmadi" emas — mijoz xatoni to'g'ri ko'rsatsin.
  Rasm OCR'dan oldin saqlanmaydi, o'qilmagan chek omborda qolmaydi.
- **Push navbati `notifications` jadvalining o'zi** (outbox): alohida broker kerak emas,
  bildirishnoma va uning push holati bitta yozuvda.
- **Eksport havolasi** har so'rovda yangi imzolanadi (5 daqiqa), lekin bir martalik
  (`downloaded_at`). Token bazada saqlanmaydi.
- **Hisobni o'chirish:** tranzaksiyasi bo'lsa — arxiv (tarix va statistika buzilmaydi).

---

## 3. Mobil uchun API o'zgarishlari (breaking)

Mobil hozircha fake datasource ishlatadi, lekin ulashda quyidagilar hisobga olinsin
(to'liq sxema — `openapi.json`):

| Eski | Yangi |
|---|---|
| `POST /auth/otp {installation_id}` → 202 `{message}` | `{device_id, attestation_token?}` → 200 `{resend_after, expires_in}` |
| `POST /auth/verify {installation_id, pin_reset}` | `{device_id, purpose: login\|pin_reset}` → `+ user {...}` |
| `invalid_code` | `otp_invalid` (+ `attempts_left`), `otp_expired` |
| `POST /auth/logout-all` | `POST /me/devices/logout-all` (joriydan tashqari) |
| `POST /auth/pin-failures` | `POST /devices/current/pin-lockout` |
| `PUT/DELETE /me/push-token` | `POST/DELETE /devices/current/push-token {token, platform}` |
| `GET /me/notifications` (massiv) | `GET /notifications` → `{items, next_cursor, unread}` |
| Tranzaksiya `{kind, category}` | `{type, category_id, title, account_id, ...}`; ro'yxat `{items, next_cursor, groups}` |
| `/budgets` CRUD | `PATCH /categories/{id} {monthly_limit}`, `GET /budgets` |
| Goal `target_amount`, `/deposit`, `/withdraw` | `target`, `/deposits`, `/withdrawals`; DELETE → `{returned_amount}` |
| Eslatma `{due_at, amount?}`, `none/daily` | `{due_date, category_id, amount}` majburiy; `once/weekly/monthly/yearly` |
| `POST /exports` → darhol URL | 202 `{id, status}` → `GET /exports/{id}` → `download_url` |
| `DELETE /me` | `POST /me/delete-code`, keyin `DELETE /me {code}` |

---

## 4. Migratsiya

`migrations/versions/20260929_b7c1e4d2a9f0_…py` — ma'lumotni saqlaydi:
tranzaksiyali userlarga "Cash" hisobi; erkin matnli kategoriya → tizim (id, en/uz/ru nomi) yoki
yangi user kategoriyasi; eski byudjetlar → `category_prefs`; eslatma sanasi Toshkent vaqtida;
bildirishnomalar → `security`. Eksport jadvali qayta yaratiladi (24 soatlik yozuvlar) —
**migratsiyadan oldin `python -m app.jobs purge`**. Downgrade yo'q (zaxiradan).
`tests/integration/test_migrations.py` eski ma'lumot bilan tekshiradi.

PG'ga xos: `roles.sql`da `CREATE EXTENSION pg_trgm` (superuser), migratsiya kengaytma bo'lsa
`title`/`note` uchun GIN trigram indeks yaratadi.

---

## 5. Scheduler (cron)

`uv run python -m app.jobs tick` — **har soat** (purge, exports, push, reminders, weekly, autosave).
Kechasi: `insights`, `rates`. Kerak bo'lganda: `reencrypt-phones`, `audit-retention`.

---

## 6. Ochiq ishlar (kod bilan hal bo'lmaydi yoki qaror kerak)

1. **OCR provayderi** (BE-701) va **Soliq ofd API** (BE-702) — ma'lumot hududi talabi (ochiq savol 3).
   Adapter `ReceiptOcr` / `FiscalReceiptProvider` portiga ~1 kunlik ish.
2. **LLM** (BE-901/903) — "o'qitishda ishlatmaslik" shartnomasi.
3. **Bank integratsiyasi** (BE-1405) — MVP'ga kiradimi?
4. **Live chat provayderi** (BE-1702), **geo-baza** (BE-105), **Play Integrity / App Attest
   verifier** va SIM-swap (BE-106).
5. **Postgres'da tekshirish:** migratsiya + `roles.sql` + `post_migrate.sql` staging'da.
6. **Yuklama testi** (`k6 run backend/loadtest/home_activity_stats.js`) staging'da, 500 RPS.
7. **Tarjimalar:** kk va tr matnlarini ona tili egasi ko'rib chiqsin.
8. Tracing (OpenTelemetry), admin panel (BE-1903), staging CI deploy.
