# Backend: tashqi integratsiyalar, bildirishnomalar, monitoring, byudjet

**Sana:** 28.09.2026
**Oldingi bosqich:** [2026-09-28-xavfsizlik-tz-davomi.md](./2026-09-28-xavfsizlik-tz-davomi.md) (commit `8e67bf2`)
**Asos:** [02-backend.md](../security/02-backend.md)

Oldingi hujjatning "Keyingi qadamlar" (11-bo'lim) ro'yxatidan kod bilan qilsa bo'ladiganlari shu
bosqichda bajarildi. Qolganlari (huquqiy, infratuzilma, GitHub sozlamasi) oxirida sababi bilan yozilgan.

| # | Qadam | Holat |
|---|---|---|
| 1 | Real SMS provayderi | ✅ Eskiz.uz adapteri |
| 2 | Push + ilova ichidagi bildirishnoma | ✅ FCM (HTTP v1) + APNs + in-app |
| 3 | S3-mos yopiq ombor + presigned URL | ✅ |
| 4 | LLM provayderi | ⏸ Shartnoma kerak (huquqiy) |
| 5 | `roles.sql`ni Postgres'da tekshirish | ⏸ Lokal Postgres yo'q |
| 6 | GitHub branch protection | ⏸ Repo sozlamasi, pastda qo'llanma bor |
| 7 | Monitoring alertlari | ✅ Prometheus metrikalar + alert qoidalari |
| 8 | Byudjet moduli | ✅ (OCR — ⏸ provayder tanlanmagan) |

---

## 1. SMS: Eskiz.uz adapteri

**Fayl:** `app/infrastructure/sms/eskiz.py`. **Sozlamalar:** `FINORA_SMS_PROVIDER=eskiz`,
`FINORA_ESKIZ_EMAIL`, `FINORA_ESKIZ_PASSWORD`, `FINORA_ESKIZ_SENDER` (standart `4546`).

- Token `POST /auth/login` orqali olinadi va xotirada saqlanadi. Provayder 401 qaytarsa, bir marta
  qayta login qilinadi va so'rov takrorlanadi. Parallel so'rovlar bir vaqtda login qilmasligi uchun
  `asyncio.Lock` ishlatiladi.
- **Loglarda SMS matni (unda OTP bor), provayder javobining tanasi va telefon raqami yo'q.** Faqat
  status kodi va xato turi yoziladi. Buni test tekshiradi: `123456` va provayderning ichki matni
  logga tushmaydi.
- Har qanday provayder xatosi mijozga `503 service_unavailable` bo'lib qaytadi. Tafsilot oshkor
  qilinmaydi (TZ 4: "xato javoblarida ichki ma'lumot yo'q").
- **Prod guard:** `sms_provider=console` bilan prod ishga tushmaydi.
- `Container.aclose()` ilova to'xtaganda HTTP klientlarni yopadi.

**Eslatma (Eskiz talabi):** SMS matni ("Finora: tasdiqlash kodi … Uni hech kimga aytmang.") Eskiz
kabinetida shablon sifatida oldindan tasdiqlangan bo'lishi kerak, aks holda SMS yuborilmaydi.

**Ma'lum cheklov:** SMS yuborilmasa ham 60 s resend limiti sarflangan bo'ladi, user bir daqiqa
kutadi. Bu ataylab qilingan: limitni SMS muvaffaqiyatiga bog'lash provayder ishlamay qolganda
limitni aylanib o'tish yo'lini ochardi.

---

## 2. Bildirishnomalar: push + ilova ichida (TZ 2-bo'lim)

TZ: *"Yangi qurilmadan kirilganda eski qurilmalarga **push va ilova ichida** bildirishnoma
yuboriladi"*, *"reuse bo'lsa … user 'New sign-in' bildirishnomasini oladi"*. Oldin `LogNotifier`
hodisani faqat loglardi. U endi o'chirildi, o'rniga `AppNotifier` keldi.

### Oqim (`app/application/notifications/notifier.py`)

1. **Ilova ichidagi yozuv har doim saqlanadi** (`notifications` jadvali). Push yetib bormasa ham user uni ko'radi.
2. Push faqat token bor qurilmalarga yuboriladi:
   - `new_sign_in`: faol sessiyali qurilmalarga, **yangi qurilmaning o'zidan tashqari**;
   - `sessions_revoked` (refresh reuse, 5 xato PIN): sessiyalar allaqachon bekor bo'lgani uchun token bor barcha qurilmalarga.
3. **Push matni umumiy**: "Hisobingizga yangi qurilmadan kirildi". Qurilma nomi faqat ilova
   ichidagi matnda bor. Sabab: push qulflangan ekranda ko'rinadi, qurilma nomida esa ko'pincha
   egasining ismi bo'ladi ("Jahongir's iPhone").
4. Push xatosi login yoki refresh'ni **yiqitmaydi**. Umumiy 5 s timeout bor, xatolar sanalib loglanadi.
5. Provayder token yaroqsiz desa (FCM `UNREGISTERED`/404, APNs 410/`BadDeviceToken`), token bazadan
   o'chiriladi va keyingi safar unga yuborilmaydi.

### Adapterlar

- **FCM HTTP v1** (`app/infrastructure/push/fcm.py`): OAuth2 access token service account kaliti
  bilan imzolangan JWT (RS256) orqali olinadi va ~1 soat keshlanadi. Eski "legacy server key" API
  ishlatilmaydi, chunki Google uni o'chirgan.
- **APNs** (`app/infrastructure/push/apns.py`): token-based auth (`.p8`, ES256 JWT, 50 daqiqa
  keshlanadi), HTTP/2 (`httpx[http2]`). Token faqat alfanumerik bo'lishi tekshiriladi, shunda
  URL yo'liga boshqa segment qo'shib bo'lmaydi (test bor).
- `RoutingPushSender` token provayderiga qarab FCM yoki APNs'ga yo'naltiradi.
- **Prod guard:** kamida bitta push provayderi (FCM yoki APNs) sozlanmagan bo'lsa, prod ishga tushmaydi.

### Endpointlar

| Metod | Yo'l | Izoh |
|---|---|---|
| `PUT` | `/v1/me/push-token` | `{provider: fcm\|apns, token}`. Faqat **joriy** qurilmaga yoziladi (device_id tokendan olinadi) |
| `DELETE` | `/v1/me/push-token` | Joriy qurilmaning tokenini o'chiradi |
| `GET` | `/v1/me/notifications?limit=` | Faqat o'z bildirishnomalari |
| `POST` | `/v1/me/notifications/{id}/read` | Begona id → 404 |

**Qaror: bitta push token faqat bitta qurilma yozuvida turadi.** Telefonda boshqa akkauntga
kirilsa, token eski akkauntning qurilma yozuvidan olib tashlanadi. Aks holda birinchi akkaunt
egasining bildirishnomalari ikkinchi odamning telefoniga borardi (test bor).

**DB:** `devices.push_provider`, `devices.push_token` (indeksli), yangi `notifications` jadvali.
Akkaunt o'chirilganda bildirishnomalar ham o'chadi. Push token API javoblarida qaytarilmaydi,
loglanmaydi ham.

---

## 3. S3-mos yopiq ombor (TZ 5, 6-bo'limlar)

**Fayl:** `app/infrastructure/storage/s3.py`. **Sozlamalar:** `FINORA_S3_BUCKET`,
`FINORA_S3_ENDPOINT_URL`, `FINORA_S3_REGION`, `FINORA_S3_KMS_KEY_ID`.

- Har bir obyekt server tomonda shifrlanadi: KMS kaliti berilsa `aws:kms`, aks holda `AES256` (TZ 5: "AES-256, kalitlar KMS'da").
- `endpoint_url` O'zbekistondagi S3-mos provayder uchun (TZ 5: ma'lumotlar O'zbekiston hududida saqlanishi).
- **Presigned GET URL:** `FileStorage` portiga `presigned_get_url()` qo'shildi. S3 URL qaytaradi,
  lokal disk `None` qaytaradi va unda oldingi HMAC endpoint ishlatiladi. `ReceiptService.sign_url`
  avval ombordan URL so'raydi, `POST /v1/receipts/{id}/url` javobining formati esa o'zgarmadi.
  URL 5 daqiqa amal qiladi, SigV4 bilan imzolanadi va `Cache-Control: no-store` bilan qaytadi.
- boto3 sinxron, shuning uchun barcha chaqiruvlar `asyncio.to_thread`da.
- **Prod guard:** `FINORA_S3_BUCKET` yo'q bo'lsa, prod ishga tushmaydi (lokal diskka yozmaslik uchun).

**Testda topilgan nozik joy:** boto3 klienti `signature_version="s3v4"`siz yaratilsa, presigned URL
eskirgan SigV2 bilan imzolanadi. Adapter klientni har doim `s3v4` bilan yaratadi.

**Bucket'ning o'zi** (public access block, versioning, lifecycle) infratuzilmada sozlanadi.
Kod faqat to'g'ri ishlatadi.

---

## 4. Monitoring va alertlar (TZ 9-bo'lim)

TZ: *"Alertlar: OTP xatolari keskin oshsa, refresh reuse bo'lsa, bitta IP'dan ko'p raqam kelsa."*
Oldin bular faqat log hodisalari edi.

### Metrikalar (`app/core/metrics.py`)

- `finora_security_events_total{event}`: mavjud log yozuvlaridan sanaladi (`SecurityEventCounter`
  log handler). Log nomi oq ro'yxatda bo'lsa hisoblagich oshadi. Kodga yangi chaqiruvlar
  qo'shilmadi, shuning uchun loglar bilan metrikalar hech qachon ajralib qolmaydi.
  Hodisalar: `otp_sent`, `otp_invalid`, `otp_blocked`, `otp_ip_limit_exceeded`,
  `refresh_token_reuse`, `receipt_malware_detected`, `sms_*`, `push_*`, `unhandled_error`.
- `finora_http_responses_total{status}` va `finora_rate_limited_total{scope}`.
- **Label'larda PII yo'q:** telefon, IP va user_id label bo'lmaydi, faqat oq ro'yxatdagi nomlar
  ishlatiladi. Bu kardinallik portlashining ham oldini oladi. Test `/metrics` chiqishida raqam
  yo'qligini tekshiradi.

### `/metrics` endpointi

- `FINORA_METRICS_TOKEN` o'rnatilgandagina yoqiladi, `Authorization: Bearer …` shart
  (constant-time taqqoslash). Token yo'q bo'lsa 404.
- Prometheus pod'ga klaster ichidan HTTP orqali murojaat qiladi, shuning uchun `/metrics` HTTPS
  majburiyligidan ozod qilingan. **Gateway bu yo'lni tashqariga chiqarmasligi kerak.** Bearer
  token qo'shimcha himoya qatlami.
- Bitta konteynerda bitta uvicorn worker (masshtab replikalar orqali), aks holda
  `prometheus_client` multiprocess rejimi kerak bo'ladi.

### Alert qoidalari: `deploy/monitoring/alerts.yml`

| Alert | Shart | Daraja |
|---|---|---|
| `FinoraOtpFailureSpike` | 10 daq ichida >50 xato kod **va** kechagi shu vaqtdan ~3 baravar ko'p | critical |
| `FinoraOtpBlocks` | 15 daq ichida >10 raqam bloklangan | warning |
| `FinoraOtpIpFlood` | IP limiti ishga tushgan (bitta IP'dan ko'p raqam) | warning |
| `FinoraRefreshTokenReuse` | har qanday reuse | warning |
| `FinoraRefreshTokenReuseMass` | 15 daq ichida >10 reuse — token bazasi sizgan bo'lishi mumkin | critical |
| `FinoraMalwareUpload` | zararli chek | warning |
| `FinoraSmsProviderFailing` | 5 daq ichida >5 SMS xatosi — userlar kira olmaydi | critical |
| `FinoraHigh5xx` | 5xx > 2% | critical |
| `FinoraRateLimitSurge` | doira bo'yicha 429 keskin oshgan | warning |

Chegara qiymatlari boshlang'ich taxmin. Real trafik ko'ringach, 1–2 haftada moslashtirish kerak.

---

## 5. Byudjetlar

**Endpointlar:** `POST/GET /v1/budgets`, `GET/PATCH/DELETE /v1/budgets/{id}`.

- Kategoriya bo'yicha oylik limit. **`spent` saqlanmaydi**, joriy oy xarajat tranzaksiyalaridan
  serverda hisoblanadi. Bu `saved` bilan bir xil tamoyil (TZ 3: mijoz hisoblangan maydonni
  yubora olmaydi). `spent` yuborilsa → 422.
- **Oy chegarasi Toshkent vaqti bo'yicha (UTC+5)**: 31-dekabr 23:30 da qilingan xarajat
  dekabrga tushadi, UTC bo'yicha hisoblaganda esa yanvarga tushib ketardi. O'zbekistonda yozgi
  vaqt yo'q, shuning uchun `tzdata`ga bog'liq bo'lmaslik uchun qat'iy offset ishlatildi (slim Docker
  image'da `tzdata` bo'lmasligi mumkin).
- Bir kategoriyaga ikkita byudjet → `409 conflict` (DB `UNIQUE (user_id, category)`).
- IDOR → 404, `Idempotency-Key` majburiy, akkaunt o'chirilganda byudjetlar ham o'chadi.

---

## 6. Migratsiya

`migrations/versions/20260928_5a24b90a75ad_notifications_push_tokens_budgets.py`:
`budgets` va `notifications` jadvallari, `devices.push_provider/push_token` ustunlari.
SQLite'da `upgrade → check → downgrade base → upgrade` tekshirildi.
Postgres'da default privileges tufayli `finora_app` yangi jadvallarga avtomatik DML huquqini oladi.

---

## 7. Bog'liqliklar

| Paket | Nega |
|---|---|
| `httpx[http2]` (dev'dan asosiyga o'tdi) | Eskiz, FCM, APNs (APNs HTTP/2 talab qiladi) |
| `boto3` (+ dev: `boto3-stubs[s3]`) | S3-mos ombor, presigned URL |
| `prometheus-client` | Metrikalar |

Linux to'plamida `pip-audit`: zaiflik yo'q. `bandit -ll`: toza.

---

## 8. Testlar

56 → **77** test, hammasi o'tadi, tarmoqqa chiqmaydi:

- `tests/unit/test_adapters.py`: Eskiz (bir marta login, 401'da qayta login, xatolar 503 bo'lib
  qaytadi va OTP logga tushmaydi), FCM (token keshi, `UNREGISTERED`), APNs (410, path injection),
  S3 (SSE-KMS parametrlari, `NoSuchKey`, SigV4 presigned URL). `httpx.MockTransport` va botocore
  `Stubber` ishlatildi.
- `tests/integration/test_notifications.py`: yangi kirish boshqa qurilmaga push va in-app yuboradi
  (o'ziga emas, push'da qurilma nomi yo'q), reuse'da push, yaroqsiz token tozalanishi, begona
  bildirishnoma → 404, token akkauntlar orasida ko'chishi, validatsiya.
- `tests/integration/test_metrics.py`: token talabi, hodisalar sanalishi, PII yo'qligi.
- `tests/integration/test_budgets.py`: `spent` hisoblanishi (eski oy kirmaydi), mass assignment,
  409, IDOR, Toshkent oy chegarasi.
- `tests/unit/test_domain.py`: prod'da SMS, push va S3 sozlanmagan bo'lsa ilova ishga tushmaydi.

---

## 9. Bajarilmagan qadamlar va sababi

1. **LLM provayderi.** TZ 8: "provayder bilan shartnomada ma'lumotni o'qitishda ishlatmaslik
   sharti" MUST. Bu huquqiy qaror, kod bilan hal bo'lmaydi. Shartnomadan keyin `InsightsModel`
   porti uchun adapter yozish ~1 soatlik ish.
2. **`roles.sql` / `post_migrate.sql`ni Postgres'da tekshirish.** Bu mashinada Postgres ham, Docker
   ham yo'q. Staging'da birinchi deployda: `roles.sql` → `alembic upgrade head` (owner) →
   `post_migrate.sql`, keyin `finora_app` bilan `DROP TABLE users;` va `UPDATE audit_log …`
   xato berishini tekshirish kerak.
3. **GitHub branch protection.** Bu repo sozlamasi, tashqi tizimga yoziladi, shuning uchun o'zim
   o'zgartirmadim. Qo'lda yoki `gh` bilan yoqish mumkin:
   `Settings → Branches → main → Require status checks: test, sca, secrets, container`.
4. **Chek OCR (summa/do'kon).** Provayder (Google Vision, lokal Tesseract va h.k.) tanlanmagan.
   Tanlashda TZ 5-bo'lim (ma'lumot hududda qolishi) muhim: chek rasmi xorijiy xizmatga
   yuborilishi shaxsiy ma'lumotni chet elga chiqarish degani. Shuning uchun bu qaror sizniki.
5. **Infratuzilma:** bucket sozlamalari, WAF, Vault, Prometheus/Alertmanager deploy'i, VPN+MFA.
