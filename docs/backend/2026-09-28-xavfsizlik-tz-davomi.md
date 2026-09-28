# Backend: Xavfsizlik TZ bo'yicha ishning davomi

**Sana:** 28.09.2026
**Asos:** [01-umumiy.md](../security/01-umumiy.md), [02-backend.md](../security/02-backend.md)
**Boshlang'ich holat:** `ed86213 feat:(Backend): project backend set up done`

Bu hujjatda shu sessiyada qilingan har bir ish, uning sababi va qabul qilingan qarorlar yozilgan.
Oxirida TZ bandlari bo'yicha holat jadvali va ochiq qolgan ishlar ro'yxati bor.

---

## 0. Boshlang'ich tahlil: nima bor edi, nima yo'q edi

Kod Clean Architecture bo'yicha qurilgan (`domain` → `application` → `infrastructure` / `presentation`,
`container.py` — DI). Oldingi bosqichda quyidagilar qilingan edi:

- OTP (CSPRNG, HMAC xesh, 120 s, 5 urinish → 15 daq blok, resend/soat/kun limitlari, bir xil javob)
- ES256 access token, opaque refresh + rotation + reuse detection, qurilma kaliti bilan imzolangan refresh
- Qurilmalar ro'yxati, logout, logout-all, PIN xatolari, "Forgot PIN?"
- Goals, transactions, exports (CSV formula injection, bir martalik havola), akkauntni o'chirish
- Xavfsizlik middleware (HTTPS, HSTS, body limit), yagona xato formati, log maskalash, audit log

**Yo'q edi:** cheklar (receipts), AI insights, eslatmalar (reminders), migratsiyalar, bazaning minimal
huquqli rollari (model izohida `deploy/db/roles.sql` deb yozilgan, lekin fayl yo'q edi), tozalash
vazifasi (eksport `purge_expired` bor, lekin uni hech narsa chaqirmas edi), CI, Dockerfile.

**Muhim topilma:** mavjud test to'plami **qizil** edi: 38 tadan 20 tasi yiqilardi, ruff 16 xato,
mypy 54 xato berardi. Shuning uchun yangi ish qo'shishdan oldin avval shu tuzatildi (1-bo'lim).

---

## 1. Mavjud kodni "yashil" holatga keltirish

### 1.1. `FOREIGN KEY constraint failed`: 20 ta test yiqilishining sababi

**Nima bo'ldi:** o'rnatilgan SQLAlchemy **2.1.1** (`>=2.0.32` cheklovi 2.1 ni ham ruxsat beradi).
Modellarda `relationship()` yo'q, faqat `ForeignKey` bor. Bunday holatda unit-of-work flush paytida
INSERT tartibini FK bo'yicha kafolatlamaydi. Natijada `devices` jadvaliga `users`dan oldin yozildi.

**Qanday tuzatildi:** ota qator yaratadigan repository `add()` metodlariga `await session.flush()`
qo'shildi (users, devices, sessions, refresh_tokens, goals, exports). Kodda bu pattern allaqachon
bor edi (`transactions.add`, `goals.add_entry`).

**Nega `relationship()` qo'shilmadi:** domen entity'lari ORM'dan ajratilgan, repository'lar
dataclass'larni qo'lda map qiladi. `relationship()` faqat tartib uchun kerak bo'lardi va
lazy-load kabi keraksiz xulqni olib kirardi. Aniq `flush()` soddaroq va ko'zga ko'rinadi.

**Fayllar:** `app/infrastructure/db/repositories/{users,auth,goals,exports}.py`

### 1.2. 3 ta test: login helper 60 s resend limitiga tushardi

`test_logout_all_and_devices_list`, `test_relogin_...`, `test_delete_account_...` bir raqam bilan
ketma-ket ikki marta login qiladi. Ikkinchi `POST /auth/otp` **to'g'ri** tarzda 429 qaytardi,
chunki TZ talabi "qayta yuborish 60 s dan keyin". Xato kodda emas, testda edi.

**Tuzatish:** `tests/conftest.py::login()` muvaffaqiyatli verify'dan keyin `InMemoryKeyValueStore`
vaqtini `otp_resend_seconds + 1` ga suradi (bu mexanizm `test_resend_after_60s_allowed`da allaqachon
bor edi). Limit mantiqi o'zgarmadi.

### 1.3. mypy (54 xato) va ruff (16 xato)

- **`SqlAlchemyUnitOfWork` `UnitOfWork` protokoliga mos kelmasdi.** Protocol atributlari invariant,
  shuning uchun `SqlAuditRepository` ≠ `AuditRepository`. Tuzatish: UoW klassida atributlar port
  tiplari bilan e'lon qilindi. Bu faqat tip darajasidagi o'zgarish, runtime'ga ta'sir qilmaydi.
- `ForeignKey(..., **_CASCADE)` tipsiz edi. Uning o'rniga tipli `_fk(target)` helper qo'shildi.
- `Depends()` default argumentda edi (B008). `TokenIssuerDep = Annotated[...]`ga o'tkazildi.
- `token_type = "Bearer"` (S105 false positive) izoh bilan `noqa` qilindi. Uzun qatorlar bo'lindi,
  keraksiz importlar olib tashlandi.

**Natija:** 38/38 test, ruff 0, mypy 0.

---

## 2. Cheklar (receipts): 02-backend.md, 4 va 6-bo'limlar

### Endpointlar

| Metod | Yo'l | Izoh |
|---|---|---|
| `POST` | `/v1/receipts/scan` | Tana: xom rasm baytlari, ≤ 10 MB. `Idempotency-Key` majburiy. 30/soat |
| `GET` | `/v1/receipts` | Faqat o'z cheklari |
| `GET` | `/v1/receipts/{id}` | Begona chek → 404 |
| `POST` | `/v1/receipts/{id}/url` | 5 daqiqalik imzolangan URL qaytaradi |
| `GET` | `/v1/receipts/{id}/image?exp=&sig=` | Imzo tekshiriladi, keyin rasm beriladi (auth header'siz) |
| `DELETE` | `/v1/receipts/{id}` | Yozuv va fayl o'chiriladi |

### Yuklash quvuri va har bir qadam sababi

1. **Rate limit 30/soat/user.** TZ jadvalidagi qiymat.
2. **Hajm ≤ 10 MB.** Middleware endi 10 MB ni faqat aynan `/v1/receipts/scan` yo'liga beradi.
   Oldin `startswith("/v1/receipts")` edi, ya'ni `/v1/receipts/{id}/url` kabi boshqa endpointlarga
   ham 10 MB ruxsat berilardi. TZ bo'yicha "chek rasmi uchun **alohida endpoint**".
3. **Magic bytes.** Format `Content-Type`ga emas, fayl boshidagi baytlarga qarab aniqlanadi
   (JPEG `FF D8 FF`, PNG `89 50 4E 47…`, HEIC `ftyp` + brand). Noma'lum format → 415.
   Sabab: `Content-Type`ni mijoz o'zi yozadi, unga ishonib bo'lmaydi.
4. **Antivirus.** `MalwareScanner` porti orqali. Prod'da ClamAV (`clamd` INSTREAM protokoli,
   qo'shimcha kutubxonasiz). **Fail-closed:** skaner xato qaytarsa yoki javob tushunarsiz bo'lsa,
   fayl qabul qilinmaydi. Topilganda `alert.malware` log hodisasi yoziladi. Dev/test'da `NoopScanner`
   ishlatiladi va u prod'da ishga tushmaydi. Prod'da `FINORA_CLAMAV_HOST` majburiy (config guard).
5. **EXIF/GPS'ni olib tashlash: rasmni qayta kodlash.** Pillow (+ `pillow-heif`) bilan ochiladi,
   EXIF orientatsiyasi piksellarga qo'llanadi, keyin **metadata'siz JPEG** sifatida saqlanadi.
   - *Nega EXIF segmentlarini qo'lda kesish emas:* qayta kodlash EXIF, GPS, XMP, ICC, maker-note
     va rasm ichiga yashirilgan "polyglot" payload'larni birdaniga yo'qotadi. Segment kesish har bir
     format uchun alohida parser talab qiladi va narsalarni o'tkazib yuborish xavfi bor.
   - *Nega hammasi JPEG'ga:* HEIC'ni ko'p klientlar ko'rsata olmaydi, bitta format esa serve
     qilishni va tekshirishni soddalashtiradi.
   - **Decompression bomb:** o'lcham header'dan o'qiladi va `width*height > 40 MP` bo'lsa, piksellar
     yuklanmasdan rad etiladi. Pillow'ning `DecompressionBombWarning`i ham xato sifatida ushlanadi.
     Natija 4096 px'dan katta bo'lmaydi.
   - Buzilgan yoki format mos kelmaydigan fayl (masalan JPEG sarlavhali "garbage") → 422 `file_rejected`.
     Aniq sabab mijozga aytilmaydi.
6. **Yopiq omborga yozish:** `receipts/{user_id}/{uuid7}.jpg`. DB yozuvi muvaffaqiyatsiz bo'lsa,
   fayl o'chiriladi.
7. **Idempotency:** barmoq izi rasm baytlarining SHA-256 xeshi. Mobil tarmoq uzilib qayta yuborsa,
   dublikat chek yaratilmaydi.

### Imzolangan URL

- `HMAC-SHA256(url_signing_key, "receipt:{id}:{exp}")`. Muddat imzoning ichida, shuning uchun
  `exp`ni o'zgartirib muddatni uzaytirib bo'lmaydi (test bor). Taqqoslash constant-time.
- Noto'g'ri imzo, eskirgan imzo va mavjud bo'lmagan chek uchun javob bir xil: **404**.
- **Nega alohida `UrlSigner` porti:** prod'da S3-mos yopiq bucket'ning presigned URL'i bilan
  almashtiriladi. Hozirgi HMAC + endpoint esa dev va `LocalFileStorage` uchun.
- Yangi kalit `FINORA_URL_SIGNING_KEY` prod guard'ga qo'shildi: standart qiymat bilan prod ishga tushmaydi.

### Akkauntni o'chirish

`DeleteAccount` endi chek fayllarini ham o'chiradi, `users.purge` esa `receipts` va `reminders`
jadvallarini tozalaydi (TZ 5-bo'lim: "barcha shaxsiy ma'lumot, **cheklar** va eksportlar").

**Fayllar:** `app/domain/receipts/*`, `app/application/receipts/use_cases.py`,
`app/infrastructure/files/{images,antivirus}.py`, `app/infrastructure/security/url_signer.py`,
`app/infrastructure/db/repositories/receipts.py`, `app/presentation/api/v1/receipts.py`,
`app/presentation/schemas/receipts.py`

**Yangi bog'liqliklar:** `pillow>=11`, `pillow-heif>=0.18` (HEIC dekodlash uchun).

---

## 3. Eslatmalar (reminders)

TZ qabul mezonlarida "boshqa user resursiga so'rov → 404 (…, **reminders**, …)" bor, lekin modul
yo'q edi. CRUD goals bilan bir xil qoidalarda qo'shildi:

- Egalik repository darajasida (`WHERE id = :id AND user_id = :sub`), begona eslatma → 404.
- `StrictModel`: `user_id` kabi noma'lum maydonlar → 422 (mass assignment).
- `title` ≤ 64, `amount` 0 < x ≤ 10¹², `due_at` faqat timezone bilan, `repeat` enum.
- `POST` `Idempotency-Key` talab qiladi (goals.create bilan bir xil yondashuv).
- `PATCH`da `"amount": null` summani olib tashlaydi, maydon yuborilmasa o'zgarmaydi.
- DB darajasida ham `CHECK` constraint'lar bor.

**Fayllar:** `app/domain/reminders/*`, `app/application/reminders/use_cases.py`,
`app/infrastructure/db/repositories/reminders.py`, `app/presentation/api/v1/reminders.py`,
`app/presentation/schemas/reminders.py`

---

## 4. AI insights: 02-backend.md, 8-bo'lim

`POST /v1/ai/ask`, tana: `{ "question": "..." }` (≤ 300 belgi). Limit: 20/soat va 100/kun (user).

- **Modelga faqat jamlangan summalar ketadi:** oxirgi 30 kun, xarajatlar kategoriya bo'yicha
  (`totals_by_category`), eng ko'pi 30 kategoriya. Alohida tranzaksiyalar, izohlar (`note`), ism,
  telefon va cheklar yuborilmaydi (test izohning modelga bormasligini tekshiradi).
- **Savoldagi PII tozalanadi.** Foydalanuvchi savolga o'zi karta yoki telefon raqamini yozishi
  mumkin. 7+ raqamli ketma-ketliklar `[raqam]`ga, email'lar `[email]`ga almashtiriladi.
  Kategoriya nomlariga ham shu qo'llanadi.
- **Javob oddiy matn:** HTML teglar, markdown havolalar, URL'lar (`http`, `javascript:`, `data:`,
  `intent:` …) va boshqaruv belgilari kesiladi, uzunlik ≤ 2000. Tool call'lar ishlatilmaydi,
  port faqat `str` qaytaradi.
- System prompt foydalanuvchi savolidagi ko'rsatmalar qoidalarni bekor qilmasligini aytadi
  (prompt-injection'ga qarshi qo'shimcha qatlam). Asosiy himoya esa yuqoridagi chiqish filtri.
- `question`/`answer` log maskalash ro'yxatiga qo'shildi.

**Muhim qaror: tashqi LLM hozircha ulanmadi.** `InsightsModel` porti va lokal `RuleBasedInsightsModel`
(tashqi so'rovsiz, jamlangan summalardan oddiy maslahat) qo'shildi. TZ 8-bo'lim bo'yicha provayder
bilan shartnomada "ma'lumotni o'qitishda ishlatmaslik" sharti bo'lishi **MUST**. Bu huquqiy qaror,
shuning uchun real provayder adapteri shartnomadan keyin shu port orqali qo'shiladi (`container.py`da TODO).

**Fayllar:** `app/application/insights/use_cases.py`, `app/infrastructure/ai/local.py`,
`app/presentation/api/v1/ai.py`, `app/presentation/schemas/insights.py`

---

## 5. Migratsiyalar va minimal huquqli baza: 02-backend.md, 5 va 9-bo'limlar

### Alembic

- `alembic.ini`, `migrations/env.py` (async), boshlang'ich migratsiya
  `migrations/versions/20260928_fd0f35334881_initial_schema.py` (12 jadval).
- URL **faqat** `FINORA_MIGRATIONS_DATABASE_URL`dan olinadi (owner roli). Ilova URL'i
  (`FINORA_DATABASE_URL`, `finora_app`) ishlatilmaydi. Sabab: ilova roli DDL qila olmasligi kerak.
- `UTCDateTime` migratsiyada oddiy `sa.DateTime(timezone=True)` bo'lib yoziladi, shunda migratsiya
  fayllari ilova kodiga bog'lanmaydi.
- SQLite'da `upgrade head`, `alembic check` (model ↔ migratsiya farqi yo'q) va `downgrade base`
  tekshirildi. CI ham `alembic check`ni ishga tushiradi.

### `deploy/db/roles.sql` (DBA, bir marta)

- `finora_owner`: sxema egasi, faqat migratsiyalar uchun.
- `finora_app`: faqat `SELECT/INSERT/UPDATE/DELETE`, `CREATE/DROP/ALTER/TRUNCATE` yo'q.
  `public` sxemadan `PUBLIC` huquqlari olinadi, kelajakdagi jadvallar uchun `DEFAULT PRIVILEGES` beriladi.
- `statement_timeout = 15s`, `idle_in_transaction_session_timeout = 30s`: uzun so'rov yoki
  qulf orqali DoS'ga qarshi.
- Parollar `psql -v` orqali Vault'dan beriladi, faylda parol yo'q.

### `deploy/db/post_migrate.sql` (har migratsiyadan keyin, owner)

- `audit_log`: `finora_app`ga **faqat INSERT** (o'qish ham yo'q).
- `BEFORE UPDATE` trigger audit yozuvini o'zgartirishni butunlay taqiqlaydi (owner uchun ham).
- `BEFORE DELETE` trigger faqat 1 yildan eski yozuvlarni o'chirishga ruxsat beradi
  (TZ: "o'zgartirib bo'lmaydigan saqlash, 1 yil").

> ⚠️ Lokal muhitda PostgreSQL yo'q edi, shuning uchun bu ikki SQL fayl **real Postgres'da ishga
> tushirib ko'rilmagan**. Staging'da birinchi deploy paytida tekshirish kerak.

---

## 6. Tozalash vazifasi: `python -m app.jobs purge`

- Muddati o'tgan yoki yuklab olingan eksport fayllari va yozuvlari o'chiriladi (TZ 6: "24 soatdan
  keyin o'chiriladi"). Oldin `purge_expired()` bor edi, lekin uni hech narsa chaqirmas edi.
- 24 soatdan eski `idempotency_keys` o'chiriladi (TZ 4: "kalit 24 soat saqlanadi").
- Cron / Kubernetes CronJob orqali soatiga bir marta ishga tushiriladi. Test: 25 soatdan keyin
  eksport ham, kalit ham o'chadi.

**Fayl:** `app/jobs.py`

---

## 7. CI, Dockerfile, secret'lar: 01-umumiy.md 4-bo'lim, 02-backend.md 9-bo'lim

`.github/workflows/backend.yml` (har PR va `main`ga push):

| Job | Nima qiladi | TZ talabi |
|---|---|---|
| `test` | ruff (flake8-bandit `S` qoidalari bilan), mypy strict, bandit `-ll`, pytest, `alembic check` | SAST, avtomatik testlar |
| `sca` | `uv export` → `pip-audit --strict` | Bog'liqliklar skaneri |
| `secrets` | gitleaks, butun git tarixi bo'yicha | Secret-scan |
| `container` | Docker build + Trivy, CRITICAL/HIGH bo'lsa yiqiladi | Konteyner skaneri |

"Yashil bo'lmasa merge yo'q" talabi uchun GitHub'da branch protection'da shu job'lar **required**
qilib belgilanishi kerak. Bu repo sozlamasi, uni kod bilan qilib bo'lmaydi.

**Dockerfile:** multi-stage, `uv sync --frozen --no-dev`, non-root (`uid 10001`), `FINORA_ENV=prod`
(prod guard'lar ishlaydi), `--proxy-headers`, `--no-server-header`. `.dockerignore` `.env`, testlar
va lokal bazalarni image'ga kiritmaydi.

**`.env.example`:** barcha kalitlar nomi, qiymatlarsiz, va kalit yaratish buyrug'i. `.env` allaqachon
`.gitignore`da.

### Topilgan zaiflik: `cryptography 48.0.1`

pip-audit uchta ma'lum zaiflik topdi (PYSEC-2026-3552/3553/3554, 49.0 / 50.0 da tuzatilgan).
Oldin `cryptography<49` cheklovi bor edi, sababi: Intel Mac'da 49+ uchun tayyor wheel yo'q.
Buni lokal ham tekshirdim: 50.0.1 da x86_64 macOS wheel yo'q.

**Qaror:** platforma markeri bilan ikkiga bo'lindi:
- Intel Mac'dan boshqa hamma joyda (Linux: CI va prod, ARM Mac) → `cryptography>=50.0`
- faqat Intel Mac (lokal dev) → `>=43,<49`

Natijada prod va CI tuzatilgan versiyada, Linux to'plamida pip-audit toza. Zaif versiya faqat
Intel Mac'dagi lokal dev muhitida qoladi. Bu ongli murosaga kelish: dev mashinani almashtirish yoki
Rust toolchain bilan build qilish boshqa yechim, lekin buni jamoa hal qiladi.

---

## 8. Mayda qo'shimchalar

- **`/.well-known/security.txt`** (RFC 9116, 01-umumiy 4-bo'lim, SHOULD). `FINORA_SECURITY_CONTACT`
  o'rnatilgan bo'lsagina yoqiladi.
- Yangi domen xatolari: `UnsupportedMediaError` (415) va `FileRejectedError` (422), yagona
  `{code, message, request_id}` formatida.
- Yangi sozlamalar: `url_signing_key`, `max_image_pixels`, `receipt_url_ttl_seconds=300`,
  `receipts_per_hour=30`, `clamav_host/port`, `ai_per_hour=20`, `ai_per_day=100`,
  `ai_question_max_length`, `ai_window_days`, `security_contact`.

---

## 9. Testlar

38 → **56** test, hammasi o'tadi. Yangi testlar:

- `test_receipts.py`: EXIF/GPS yo'qolishi, PNG/HEIC → JPEG, magic bytes (PHP payload → 415,
  soxta JPEG → 422), >10 MB → 413, antivirus rad etishi, IDOR (get/url/delete → 404), imzo
  buzilishi va `exp`ni o'zgartirish, 5 daqiqadan keyin URL → 404, idempotency, 30/soat limiti,
  akkaunt o'chirilganda fayllarning o'chishi.
- `test_reminders_ai.py`: reminders CRUD + IDOR, mass assignment, validatsiya, AI'ga faqat
  agregatlar ketishi (izoh/karta/telefon yo'q), javobdan HTML/URL/`javascript:` kesilishi,
  AI rate limit, `security.txt`.
- `test_jobs.py`: eksport va idempotency kalitlarini tozalash.

Buyruqlar: `uv run pytest -q`, `uv run ruff check .`, `uv run mypy app`,
`uv run bandit -r app -c pyproject.toml -ll`

---

## 10. TZ bandlari bo'yicha holat (02-backend.md)

| Bo'lim | Holat | Izoh |
|---|---|---|
| 1. OTP, MUST | ✅ | Oldingi bosqich |
| 1. SIM-swap, Play Integrity / App Attest (SHOULD) | ❌ | SMS provayderi va mobil tayyor bo'lganda |
| 2. Tokenlar, sessiyalar | ✅ / ⚠️ | Push bildirishnoma hozircha `LogNotifier`, FCM/APNs adapteri yo'q |
| 3. Avtorizatsiya (IDOR, UUIDv7, mass assignment, saved) | ✅ | Endi reminders va receipts ham |
| 4. Validatsiya, idempotency, xato formati, body limit | ✅ | 10 MB endi faqat `/receipts/scan` |
| 4. Rate limit jadvali | ✅ | `/receipts/scan` va `/ai/ask` qo'shildi, jadval to'liq |
| 4. TLS 1.2+, WAF (SHOULD) | ⚠️ | Ilovada HTTPS/HSTS bor. TLS versiyasi va WAF — gateway sozlamasi |
| 5. Telefonni field-level shifrlash, blind index | ✅ | Oldingi bosqich |
| 5. Disk/zaxira AES-256, KMS | ⚠️ | Infratuzilma (hosting tanlanganda) |
| 5. O'zbekistonda saqlash | ⚠️ | Hosting va yurist qarori |
| 5. Akkauntni o'chirish | ✅ | Endi cheklar ham |
| 5. Minimal huquqli DB roli | ✅ / ⚠️ | SQL yozildi, real Postgres'da tekshirilmagan |
| 6. Yopiq ombor + 5 daq imzolangan URL | ✅ / ⚠️ | Lokal HMAC. S3 adapteri (SSE-KMS, presigned) yo'q |
| 6. Magic bytes, EXIF/GPS, antivirus | ✅ | |
| 6. CSV formula injection, 24 soat, bir martalik havola | ✅ | Endi tozalash vazifasi ham bor |
| 7. PIN (server tomoni) | ✅ | Oldingi bosqich |
| 8. AI: agregatlar, oddiy matn | ✅ | |
| 8. Provayder shartnomasi | ❌ | Huquqiy qaror. Real LLM adapteri undan keyin |
| 9. Log maskalash, audit log | ✅ | Audit o'zgarmasligi endi DB trigger bilan |
| 9. Alertlar | ⚠️ | `alert.*` log hodisalari bor, monitoring qoidalari (Grafana/Sentry) sozlanmagan |
| 9. Secrets Vault, secret-scan, SAST/SCA/konteyner | ✅ / ⚠️ | CI tayyor. Branch protection va Vault — infratuzilma |

### Qabul mezonlari

- [x] Boshqa user resursiga so'rov → `404` (goals, transactions, reminders, receipts; exports token orqali)
- [x] 6-OTP urinishi → `429`, raqam 15 daqiqa bloklangan
- [x] 61 soniyadan oldin qayta SMS → `429`
- [x] Ishlatilgan refresh token qayta yuborilsa → barcha sessiya tokenlari bekor
- [x] Bir xil `Idempotency-Key` bilan 2 ta deposit → bitta yozuv
- [x] Withdraw > saved → `422`
- [x] Loglarda to'liq telefon raqami va OTP topilmaydi
- [x] CSV eksportda `=cmd` qiymati `'=cmd` bo'lib chiqadi

---

## 11. Keyingi qadamlar (ochiq ishlar)

> **Yangilanish:** 1, 2, 3, 7 va 8 (byudjet) bandlari keyingi bosqichda bajarildi:
> [2026-09-28-integratsiyalar-va-monitoring.md](./2026-09-28-integratsiyalar-va-monitoring.md)

1. **Real SMS provayderi** (Eskiz / Playmobile) — `SmsSender` porti. Prod'da `ConsoleSmsSender` ishga tushmaydi.
2. **Push** (FCM/APNs) — `Notifier` porti ("New sign-in" bildirishnomasi uchun MUST).
3. **S3-mos yopiq ombor** (SSE-KMS) + presigned URL — `FileStorage` va `UrlSigner` portlari.
4. **LLM provayderi** — shartnoma imzolangandan keyin `InsightsModel` porti orqali.
5. `roles.sql` / `post_migrate.sql`ni staging Postgres'da tekshirish, deploy pipeline'ga qo'shish.
6. GitHub branch protection: CI job'larini required qilish.
7. Monitoring: `alert.otp_failures`, `alert.otp_ip_flood`, `alert.refresh_reuse`, `alert.malware` uchun alert qoidalari.
8. Chekdan OCR (summa/do'kon) — hozir faqat rasm saqlanadi. Byudjet moduli ham hali yo'q.

### Eslatma: men qilmagan o'zgarish

`pyproject.toml`da `"starlette>=1.7.0"` qatori va `.idea/` fayllari sessiya davomida paydo bo'ldi
(ehtimol IDE qo'shgan). Men ularga tegmadim, ularni saqlash-saqlamaslikni o'zingiz hal qiling.
