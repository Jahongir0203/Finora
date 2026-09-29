# Finora — Backend tasklari

Dizayndagi har bir ekran va funksiya bo'yicha backend ishlari. Har bir task: nima qilinadi, endpointlar, qoidalar, qabul mezonlari.

Bog'liq hujjatlar: `docs/security/02-backend.md` (xavfsizlik MUST talablari), `docs/screens/*.md` (UI spetsifikatsiya).

**Umumiy kelishuvlar (barcha tasklar uchun):**
- REST, JSON, prefiks `/v1`. ID — UUIDv7. Vaqt — ISO 8601 UTC, mijoz vaqt zonasi `X-Timezone` sarlavhasida (`Asia/Tashkent`).
- Summalar butun son, asosiy valyutaning minimal birligida (so'm). `0 < amount ≤ 10^12`.
- Xato formati: `{ code, message, request_id }`. Begona resurs → `404`.
- Yozuv yaratuvchi POST'lar `Idempotency-Key` talab qiladi (24 soat).
- Ro'yxatlar cursor pagination: `?cursor=&limit=` (default 30, max 100).
- Har bir so'rovda `user_id = sub` tekshiruvi repository qatlamida.

Prioritet: **P0** — MVP uchun shart, **P1** — reliz uchun kerak, **P2** — keyinroq.

---

## 0. Infratuzilma va asos

### BE-001 · Loyiha skeleti va muhitlar · P0
- Servis skeleti, konfiguratsiya, `dev` / `staging` / `prod` muhitlari.
- PostgreSQL, Redis (rate limit, OTP, kesh), obyekt saqlash (S3-mos, yopiq bucket).
- Migratsiyalar (versiyalangan), seed skriptlari (kategoriyalar, valyutalar, tillar).
- Healthcheck: `GET /health`, `GET /ready`.
- **Qabul:** staging'ga CI orqali deploy bo'ladi; migratsiya bir buyruq bilan ishlaydi.

### BE-002 · Umumiy middleware · P0
- Request ID, strukturalangan log (token, OTP, summa, to'liq telefon loglanmaydi).
- Yagona xato formati, validatsiya xatolari `422` + maydonlar ro'yxati.
- `Idempotency-Key` middleware (Redis, 24 soat, javobni qayta qaytaradi).
- Rate limiter (jadval: `02-backend.md` 4-bo'lim).
- So'rov tanasi ≤ 1 MB.
- **Qabul:** bir xil `Idempotency-Key` bilan 2 ta POST → bitta yozuv, bir xil javob.

### BE-003 · CI/CD va xavfsizlik skanerlari · P1
- SAST, SCA, konteyner skaneri, secret-scanning. Critical/High bilan reliz bloklanadi.
- Secrets — Vault/KMS.

### BE-004 · Monitoring va alertlar · P1
- Metrikalar (latency, 5xx, rate limit hits), tracing.
- Alertlar: OTP xatolari keskin oshishi, refresh reuse, bitta IP'dan ko'p raqam.

### BE-005 · Audit log · P1
- Hodisalar: kirish, yangi qurilma, logout, PIN reset, eksport, akkaunt o'chirish.
- O'zgartirib bo'lmaydigan saqlash (append-only), 1 yil.

---

## 1. Auth: Sign in, Verify code (`AUTH_SCREENS.md`)

### BE-101 · OTP yuborish · P0
`POST /v1/auth/otp` → `{ phone: "+998901234567", device_id, attestation_token? }`
- Faqat `+998` raqamlar, 9 xona validatsiyasi.
- 6 xonali kod, CSPRNG. Bazada HMAC-SHA256 xeshi, muddati 120 s.
- Javob har doim bir xil: `{ resend_after: 60, expires_in: 120 }` (raqam ro'yxatda bor-yo'qligi oshkor qilinmaydi).
- Limit: 1/60 s, 5/soat, 10/kun (telefon + IP + qurilma alohida).
- SMS provayder integratsiyasi (Eskiz / PlayMobile), fallback provayder.
- **Qabul:** 60 s ichida qayta so'rov → `429` + `retry_after`; loglarda kod yo'q.

### BE-102 · OTP tasdiqlash · P0
`POST /v1/auth/verify` → `{ phone, code, device_id, device_public_key, device_name, platform }`
- Constant-time taqqoslash. Bitta kodga 5 urinish, keyin kod bekor + raqam 15 daqiqa blok.
- Muvaffaqiyatli: user yo'q bo'lsa yaratiladi. Javob:
  `{ access_token, refresh_token, user: { id, first_name, is_new, has_pin_setup, onboarding } }`
- `is_new` va `onboarding` mijozga keyingi ekranni tanlash uchun (Create PIN → Starting balance → Home).
- Xato javobi: `{ code: "otp_invalid", attempts_left }` — UI "Wrong code" holati uchun.
- **Qabul:** 6-urinish → `429`; ishlatilgan kod qayta ishlamaydi; muddati o'tgan kod → `otp_expired`.

### BE-103 · Tokenlar va refresh · P0
`POST /v1/auth/refresh` → `{ refresh_token }` + qurilma kaliti bilan imzo sarlavhasi.
- Access 15 daqiqa (ES256/EdDSA, payload: `sub`, `sid`, `did`, `exp`). Refresh opaque 256 bit, 30 kun, rotation.
- Reuse aniqlansa → sessiya oilasi bekor + `security` bildirishnoma.
- Muddati o'tgan → `401 session_expired` (UI: "Session expired" holati, `STATES.md`).
- **Qabul:** eski refresh ikkinchi marta → barcha sessiya tokenlari bekor.

### BE-104 · Logout · P0
`POST /v1/auth/logout` — joriy sessiya refresh tokenini serverda bekor qiladi.

### BE-105 · Yangi qurilmadan kirish bildirishnomasi · P1
- Yangi `device_id` bilan verify → boshqa qurilmalarga push + in-app `security` bildirishnoma ("New sign-in · Finora was opened on a new device in Tashkent"). Shahar — IP geolokatsiya.

### BE-106 · Play Integrity / App Attest tekshiruvi · P2
- `attestation_token` OTP so'rovidan oldin tekshiriladi. SIM-swap tekshiruvi (provayder qo'llasa).

---

## 2. PIN, Lock, Starting balance (`PIN_SETUP_SCREENS.md`)

PIN serverga yuborilmaydi va saqlanmaydi (`02-backend.md` 7-bo'lim). Backend faqat holat va hodisalarni qabul qiladi.

### BE-201 · PIN o'rnatilganini belgilash · P0
`POST /v1/me/pin-setup` → `{ device_id }` — `has_pin_setup = true` (qurilma darajasida). Mijoz onboarding oqimini to'g'ri tiklashi uchun.

### BE-202 · Xato PIN hodisasi (5 urinish) · P0
`POST /v1/devices/current/pin-lockout` (qurilma kaliti bilan imzolangan).
- Shu qurilma sessiyasi bekor qilinadi, audit log. Javobdan keyin mijoz Sign in'ga qaytadi.
- **Qabul:** imzosiz so'rov → `401`.

### BE-203 · Forgot PIN · P0
- Mijoz qayta OTP oqimidan o'tadi (BE-101/102) `purpose: "pin_reset"` bilan. Muvaffaqiyatli bo'lsa eski qurilma sessiyasi bekor, yangi sessiya, `has_pin_setup = false`.
- Audit: `pin_reset`.

### BE-204 · Starting balance · P0
`POST /v1/onboarding/balance` → `{ amount, location: "cash" | "card" | "both" }`
- `location` bo'yicha hisob(lar) yaratiladi: `cash` → "Cash" hisobi, `card` → "Card" hisobi, `both` → ikkalasi (summa birinchisiga, keyin tahrirlanadi).
- Boshlang'ich balans tranzaksiya sifatida emas, hisobning `opening_balance` maydoni sifatida saqlanadi (statistikaga kirmaydi).
- "Skip" / "I'll do it later" → hech narsa yuborilmaydi, `onboarding.balance_set = false`.
- Home'dagi "Add your current balance" sheet ham shu endpointni ishlatadi.
- **Qabul:** qayta chaqirilsa `opening_balance` yangilanadi, dublikat hisob yaratilmaydi.

### BE-205 · Auto-lock va biometriya sozlamalari · P1
`PATCH /v1/me/settings` → `{ auto_lock_minutes: 1 | 3 | 5, biometric_enabled: bool }`
- Qurilma darajasida saqlanadi (bir nechta qurilma — alohida qiymatlar). Security sheet va PIN lock chip'dagi `{n} min` shu yerdan.

---

## 3. Home (`HOME_NOTIFICATIONS.md`)

### BE-301 · Home agregat endpointi · P0
`GET /v1/home` — bitta so'rovda butun ekran:
```json
{
  "user": { "first_name": "Doston", "initials": "DK" },
  "balance": { "total": 24850000, "currency": "UZS", "need_balance": false },
  "month": { "income": 13000000, "expenses": 5460000 },
  "unread_notifications": 3,
  "get_started": { "balance": true, "transaction": false, "goal": false, "reminder": false },
  "ai_teaser": { "title": "...", "saving": 380000 } | null,
  "budget_summary": { "month": "2026-09", "spent": 5460000, "limit": 7400000 } | null,
  "upcoming_payments": [ { "id", "title", "amount", "due_date", "category_id" } ],
  "recent_transactions": [ ...4 ta ]
}
```
- `balance.total` = barcha faol hisoblar `opening_balance` + kirim − chiqim ± goal deposit/withdraw.
- Oy chegarasi foydalanuvchi vaqt zonasida.
- `ai_teaser` va `budget_summary` yangi foydalanuvchida `null` (UI yashiradi).
- `upcoming_payments` — yoqilgan eslatmalar, keyingi 14 kun, `due_date` bo'yicha.
- **Qabul:** p95 < 300 ms; yangi user uchun barcha summalar 0, ro'yxatlar bo'sh.

### BE-302 · Offline qo'llab-quvvatlash (sync) · P1
- Mijoz offline yaratgan yozuvlar `Idempotency-Key` + `client_created_at` bilan keyin yuboriladi.
- `GET /v1/sync?since=<timestamp>` — o'zgargan/o'chirilgan yozuvlar (tranzaksiya, goal, eslatma, kategoriya, hisob) delta ko'rinishida.
- **Qabul:** bir xil yozuv ikki marta sync qilinsa dublikat yo'q.

---

## 4. Notifications (`HOME_NOTIFICATIONS.md` 4-bo'lim)

### BE-401 · Bildirishnomalar ro'yxati · P0
`GET /v1/notifications` → `[{ id, type, title, body, created_at, read, deep_link }]`
- `type`: `payment_due`, `income`, `budget_exceeded`, `weekly_report`, `goal_milestone`, `security`.
- `deep_link`: `/reminders`, `/activity`, `/budgets`, `/stats`, `/profile`.
- Guruhlash (Today / Earlier) mijozda, vaqt zonasi bo'yicha.

### BE-402 · O'qilgan / tozalash · P0
- `POST /v1/notifications/{id}/read`
- `POST /v1/notifications/read-all` ("Mark all read")
- `DELETE /v1/notifications` ("Clear", soft delete)

### BE-403 · Bildirishnoma generatorlari · P1
Har bir tur uchun trigger:
| Tur | Trigger | Matn manbai |
|---|---|---|
| `payment_due` | eslatma sanasidan 1 kun oldin va shu kuni, 10:00 lokal | eslatma nomi, summa, sana |
| `income` | kirim tranzaksiya yaratilganda (bank sync yoki qo'lda emas — faqat avtomatik) | summa, manba, karta last4 |
| `budget_exceeded` | kategoriya xarajati limitdan oshgan paytda (oyda bir marta), 75% da ogohlantirish | kategoriya, spent/limit |
| `weekly_report` | har dushanba 09:00 lokal, oldingi hafta ma'lumoti bo'lsa | haftalik farq % |
| `goal_milestone` | goal 25/50/75/100% ga yetganda | goal nomi, % |
| `security` | yangi qurilma, PIN reset, barcha qurilmalardan chiqish | qurilma, shahar |
- Lokalizatsiya: foydalanuvchi tilida (BE-1102).
- `notifications_enabled = false` bo'lsa push yuborilmaydi, in-app yoziladi.

### BE-404 · Push (FCM / APNs) · P1
- `POST /v1/devices/current/push-token` → `{ token, platform }`. Logout'da o'chiriladi.
- Navbat (queue) orqali yuborish, qayta urinish, yaroqsiz tokenlarni tozalash.

---

## 5. Activity va tranzaksiyalar (`ACTIVITY_SCAN.md`)

### BE-501 · Tranzaksiya modeli · P0
Maydonlar: `id, user_id, account_id, type (expense | income | transfer), amount, currency, category_id, title, note, occurred_at, source (manual | scan | bank), receipt_id?, created_at, updated_at, deleted_at`.
- Indekslar: `(user_id, occurred_at desc)`, `(user_id, category_id, occurred_at)`.
- Matn maydonlari ≤ 64 belgi (note ≤ 256).

### BE-502 · Tranzaksiya yaratish (New transaction sheet) · P0
`POST /v1/transactions` → `{ type, amount, category_id, title?, note?, account_id?, occurred_at? }`
- `category_id` turiga mos bo'lishi shart (expense → chiqim kategoriyalari, income → Salary/Transfer va user yaratganlari).
- `account_id` berilmasa — default hisob. `occurred_at` default — hozir.
- Yaratilgandan keyin: byudjet tekshiruvi (BE-403 `budget_exceeded`), Get started holati yangilanadi.
- Javob: yaratilgan tranzaksiya + yangilangan `balance.total`.
- **Qabul:** turiga mos kelmaydigan kategoriya → `422`; `amount ≤ 0` → `422`.

### BE-503 · Tranzaksiyalar ro'yxati (Activity) · P0
`GET /v1/transactions?q=&type=&category_id=&from=&to=&cursor=`
- Filter chiplari: All / Expenses / Income / kategoriya.
- `q` — title, note va kategoriya nomi bo'yicha qidiruv (case-insensitive, trigram indeks).
- Javobda sahifa + kunlik guruh summalari: `groups: [{ date, net }]` (Today/Yesterday nomlari mijozda).
- **Qabul:** `q=evos` "Evos cafe"ni topadi; natija yo'q → bo'sh massiv, `200`.

### BE-504 · Tranzaksiyani tahrirlash va o'chirish · P1
- `PATCH /v1/transactions/{id}`, `DELETE /v1/transactions/{id}` (soft delete, sync uchun).
- Balans, byudjet va statistika qayta hisoblanadi.

### BE-505 · Hisob-kitob servisi · P0
- Hisob balansi, oylik kirim/chiqim, kategoriya bo'yicha xarajat — bitta servisda, barcha endpointlar shuni ishlatadi.
- Agregatlar keshlanadi (Redis), tranzaksiya o'zgarganda invalidatsiya.

---

## 6. Export report (`ACTIVITY_SCAN.md` 4-bo'lim)

### BE-601 · Eksport oldindan ko'rish · P0
`GET /v1/exports/preview?period=daily|weekly|monthly|yearly&include=expense,income,transfer`
→ `{ range_label, from, to, count, income, expenses, net, file_name }`
- Davrlar: Daily — bugun; Weekly — joriy ISO hafta; Monthly — joriy oy; Yearly — yil boshidan bugungacha.
- `include`dan chiqarilgan tur summasi 0.
- Fayl nomi: `finora_{period}_{part}.{ext}` (`finora_monthly_sep2026.pdf`, `w39_2026`, `28sep2026`, `2026`).

### BE-602 · Eksport yaratish · P0
`POST /v1/exports` → `{ period, include[], format: pdf | xlsx | csv }` → `{ id, status: "pending" }`
- Asinxron job (queue). `GET /v1/exports/{id}` → `{ status: pending | ready | failed, download_url?, file_name }`.
- PDF: sarlavha, davr, Income/Expenses/Net, kategoriya bo'yicha jadval, tranzaksiyalar ro'yxati. Excel: 2 varaq (Summary, Transactions). CSV: faqat tranzaksiyalar.
- CSV/Excel formula injection himoyasi (`=`, `+`, `-`, `@` oldiga `'`).
- `download_url` — imzolangan, bir martalik; fayl 24 soatdan keyin o'chiriladi.
- Xato → `status: failed, error_code` (UI "Export failed" holati).
- Limit: 10/soat. Audit log: `export`.
- **Qabul:** 712 ta tranzaksiyali yillik PDF < 10 s; bo'sh `include` → `422`.

---

## 7. Scan: chek va QR (`ACTIVITY_SCAN.md` 5-bo'lim)

### BE-701 · Chek rasmini yuklash va OCR · P0
`POST /v1/receipts/scan` (multipart, ≤ 10 MB) → `{ image }`
- MIME magic-bytes (JPEG/PNG/HEIC), EXIF/GPS olib tashlanadi, antivirus.
- OCR (provayder yoki o'z modeli): do'kon nomi, sana, jami summa, pozitsiyalar (nom, soni, narx).
- Kategoriya taxmini: do'kon nomi/pozitsiyalar bo'yicha (masalan, Korzinka → groceries).
- Javob: `{ receipt_id, merchant, total, occurred_at, items[], suggested_category_id, confidence }`.
- O'qib bo'lmasa → `422 receipt_unreadable` (UI "Couldn't read the receipt").
- Limit: 30/soat.

### BE-702 · Fiskal QR kod · P1
`POST /v1/receipts/qr` → `{ payload }` (QR matni)
- Soliq qo'mitasi fiskal chek QR'ini parse qilish va ofd.soliq.uz orqali chek ma'lumotini olish.
- QR fiskal chek emas → `422 qr_not_supported`.
- Javob BE-701 bilan bir xil format.

### BE-703 · Skanerdan tranzaksiya saqlash · P0
- "Receipt scanned" sheet'da tasdiqlanganda BE-502 `source: "scan", receipt_id` bilan chaqiriladi.
- Chek rasmi yopiq bucket'da, faqat 5 daqiqalik imzolangan URL: `GET /v1/receipts/{id}/image`.
- Tasdiqlanmagan cheklar 24 soatdan keyin o'chiriladi.

---

## 8. Statistics (`STATS_INSIGHTS.md` 1-bo'lim)

### BE-801 · Statistika endpointi · P0
`GET /v1/stats?period=week|month|year&date=2026-09-28`
```json
{
  "total_spent": 5300000,
  "change_pct": -8,
  "bars": [ { "label": "W1", "value": 1200000, "current": false } ],
  "breakdown": [ { "category_id": "groceries", "amount": 1840000, "pct": 35 } ],
  "has_enough_data": true
}
```
- Week — 7 kun (M..S), Month — 4–5 hafta (W1..W5), Year — 12 oy (kelajak oylari 0).
- `change_pct` — oldingi shunday davr bilan solishtirish.
- `breakdown` summa bo'yicha kamayish tartibida, foizlar yig'indisi 100.
- `has_enough_data = false`: birinchi tranzaksiyadan 7 kun o'tmagan (UI "Not enough data yet").
- **Qabul:** foizlar yaxlitlanganda ham yig'indi 100; faqat chiqimlar hisoblanadi.

---

## 9. AI insights (`STATS_INSIGHTS.md` 2-bo'lim)

### BE-901 · Tavsiyalar generatsiyasi · P1
`GET /v1/insights` → `{ potential_saving, items: [{ id, kind, icon, category_id?, title, body, saving?, action }] }`
- `action`: `set_budget`, `remind_me`, `review`, `turn_on_autosave`.
- Qoidaga asoslangan detektorlar (har kuni tunda hisoblanadi):
  - Kategoriya xarajati 3 oylik o'rtachadan > 20% yuqori (food, taxi/transport).
  - Chegirma kunlari naqshi (groceries).
  - Bir xil turdagi takroriy obunalar (subs).
  - Kirim bor, lekin goal'ga avtomatik jamg'arma yo'q (auto).
- Matnni LLM bilan jilolash ixtiyoriy; modelga faqat jamlangan summalar yuboriladi.
- `potential_saving` — barcha faol tavsiyalar `saving` yig'indisi + backend qo'shimcha baholash.

### BE-902 · Tavsiya amallari · P1
- `POST /v1/insights/{id}/dismiss`
- `POST /v1/insights/{id}/action` → amalga qarab: `set_budget` → byudjet yaratish/yangilash (BE-1001); `remind_me` → eslatma (BE-1201); `turn_on_autosave` → goal auto-save yoqish; `review` → `reviewed` belgisi.
- `GET /v1/insights?include_dismissed=true` ("Show dismissed").

### BE-903 · AI savol-javob · P1
`POST /v1/ai/ask` → `{ question }` → `{ answer }`
- Kontekst: oxirgi 3 oy kategoriya bo'yicha jamlangan summalar, byudjetlar, goal progress. Ism, telefon, karta raqami, chek yuborilmaydi.
- Javob oddiy matn (HTML/havola/tool call yo'q), foydalanuvchi tilida, ≤ 600 belgi.
- Moliyaviy maslahat bo'lmasligi haqida system prompt; prompt injection filtri.
- Limit: 20/soat, 100/kun. Timeout 15 s → `503 ai_unavailable`.
- Tayyor savollar ro'yxati: `GET /v1/ai/suggestions` (lokalizatsiya bilan).
- **Qabul:** p95 < 4 s; loglarda savol matni saqlanmaydi (yoki 30 kun, anonim).

---

## 10. Budgets (`BUDGETS_GOALS.md` 1-bo'lim)

### BE-1001 · Kategoriya limitlari · P0
- Limit kategoriyada saqlanadi: `PATCH /v1/categories/{id}` → `{ monthly_limit }` (null = limit yo'q).
- `GET /v1/budgets?month=2026-09` → `[{ category_id, limit, spent, pct, status: normal | warning | over, left }]`
  - `warning`: 0.75 ≤ pct ≤ 1, `over`: pct > 1.
- Yangi user uchun default limitlar qo'yilmaydi (UI "No budgets set").
- **Qabul:** oy o'tganda `spent` 0 dan boshlanadi, limit saqlanadi.

---

## 11. Goals (`BUDGETS_GOALS.md` 2–3-bo'lim)

### BE-1101 · Goal CRUD · P0
- `GET /v1/goals` → `[{ id, name, icon, target, saved, pct, deadline?, auto_save_monthly?, created_at }]`
- `POST /v1/goals` → `{ name, icon, target, deadline?, auto_save_monthly? }`
  - `name` bo'sh emas, ≤ 64; `target ≥ 100 000` — aks holda `422` (UI xato matnlari bilan mos kodlar: `goal_name_required`, `goal_target_min`).
- `PATCH /v1/goals/{id}`, `DELETE /v1/goals/{id}`.
- `saved` mijozdan qabul qilinmaydi.

### BE-1102 · Deposit / Withdraw · P0
- `POST /v1/goals/{id}/deposits` → `{ amount, account_id? }`
- `POST /v1/goals/{id}/withdrawals` → `{ amount, account_id? }` — `amount ≤ saved` serverda tekshiriladi (tranzaksiya ichida, row lock).
- `saved` = deposit − withdraw, faqat serverda. Asosiy hisob balansi mos ravishda o'zgaradi.
- `GET /v1/goals/{id}/history` — Goal details'dagi tarix.
- Milestone tekshiruvi (BE-403 `goal_milestone`).
- **Qabul:** parallel 2 ta withdraw `saved`dan oshirib yubora olmaydi.

### BE-1103 · Goal o'chirish · P0
- `DELETE /v1/goals/{id}` — `saved` summasi asosiy hisobga qaytariladi (bitta DB tranzaksiyasida), javob: `{ returned_amount }`.

### BE-1104 · Goal rejasi hisob-kitobi · P1
- Goal details va New goal sheet uchun: `monthly_needed = ceil((target − saved) / oylar_soni)`, `eta_months = ceil((target − saved) / auto_save_monthly)`.
- `GET /v1/goals/plan?target=&deadline=&auto_save=` (sheet ochiqligida jonli hisob) yoki goal javobida `plan` obyekti.

### BE-1105 · Auto-save · P2
- `auto_save_monthly` bor goal'lar uchun har oy belgilangan kuni avtomatik deposit (scheduler, idempotent: `goal_id + month`).
- Hisobda mablag' yetmasa — o'tkazib yuboriladi + bildirishnoma.

---

## 12. Payment reminders (`REMINDERS.md`)

### BE-1201 · Eslatma CRUD · P0
- `GET /v1/reminders` → `[{ id, title, category_id, amount, next_due_date, repeat: once | weekly | monthly | yearly, enabled, due_in_days }]`, `next_due_date` bo'yicha tartiblangan.
- `POST /v1/reminders` → `{ title, category_id, amount, due_date, repeat }` — `title.trim()` bo'sh emas, `amount > 0`. `enabled = true`.
- `PATCH /v1/reminders/{id}` (switch: `{ enabled }`), `DELETE /v1/reminders/{id}`.

### BE-1202 · Takrorlanish va keyingi sana · P0
- Sana o'tganda `repeat`ga qarab `next_due_date` suriladi (oy oxiri: 31 → 30/28).
- `once` — sana o'tgach avtomatik `enabled = false`.
- Kunlik scheduler, foydalanuvchi vaqt zonasida.

### BE-1203 · Eslatmani to'langan deb belgilash · P2
- `POST /v1/reminders/{id}/pay` → shu summa va kategoriyada chiqim tranzaksiyasi yaratadi, keyingi sanaga suradi.

---

## 13. Profile (`PROFILE_SETTINGS.md` 2-bo'lim)

### BE-1301 · Profil · P0
- `GET /v1/me` → `{ id, first_name, last_name, phone_masked, initials, language, currency, theme, notifications_enabled, counts: { accounts, categories, reminders_enabled } }`
- `PATCH /v1/me` → `{ first_name, last_name }` (≤ 64).
- `phone_masked`: `+998 90 *** ** 67`.

### BE-1302 · Sozlamalar · P0
`PATCH /v1/me/settings` → `{ language, currency, theme: light | dark | system, notifications_enabled }`
- Dark mode mijozda darhol, serverga sinxron (boshqa qurilmalar uchun).

### BE-1303 · Faol qurilmalar · P1
- `GET /v1/me/devices` → `[{ id, name, platform, city, last_active_at, current }]`
- `DELETE /v1/me/devices/{id}` — shu qurilma sessiyasini bekor qiladi.
- `POST /v1/me/devices/logout-all` — joriydan tashqari hammasi. `security` bildirishnoma.

### BE-1304 · Akkauntni o'chirish · P1
- `DELETE /v1/me` (qayta OTP tasdig'i bilan). 30 kun ichida barcha shaxsiy ma'lumot, cheklar, eksportlar o'chiriladi. Audit log.

---

## 14. Accounts & cards (`PROFILE_SETTINGS.md` 4-bo'lim)

### BE-1401 · Hisoblar modeli va ro'yxati · P0
- Maydonlar: `id, type (card | cash | bank_account), bank_name, network (UZCARD | HUMO | VISA | MASTERCARD), last4, expiry, color, opening_balance, monthly_limit?, frozen, is_default`.
- To'liq karta raqami **saqlanmaydi** — faqat `last4` va `expiry`.
- `GET /v1/accounts` → `{ total, count, items: [{ ..., balance }] }` (Accounts ekrani "Total across 4 accounts").

### BE-1402 · Hisob qo'shish / tahrirlash · P0
- `POST /v1/accounts` → `{ type, bank_name?, network?, last4?, expiry?, color?, opening_balance }`
- `PATCH /v1/accounts/{id}`, `DELETE /v1/accounts/{id}` (tranzaksiyalari bor bo'lsa soft delete / arxiv).

### BE-1403 · Freeze / Unfreeze · P1
- `POST /v1/accounts/{id}/freeze`, `/unfreeze`. Muzlatilgan hisobga yangi tranzaksiya yozilmaydi (`422 account_frozen`).
- Eslatma: bu faqat Finora ichidagi belgi. Haqiqiy bank kartasini muzlatish bank integratsiyasini talab qiladi (BE-1405).

### BE-1404 · O'tkazma (Transfer) · P1
- `POST /v1/transfers` → `{ from_account_id, to_account_id, amount }` — ikki bog'langan `transfer` yozuvi, statistikada xarajat emas.

### BE-1405 · Bank integratsiyasi va sync · P2 · ochiq savol
- Dizaynda "Bank sync failed · Kapitalbank did not respond" holati va `income` bildirishnomasi ("arrived on Uzcard •• 4821") bor, lekin Starting balance'da "Finora doesn't connect to your bank" deyilgan.
- Qaror kerak: bank/processing (Uzcard/Humo) integratsiyasi MVP'ga kiradimi? Kirsa: ulash (`POST /v1/accounts/{id}/connect`), davriy sync job, `sync_status`, `last_synced_at`, xato → `sync_failed` holati va Home banner.

---

## 15. Categories (`PROFILE_SETTINGS.md` 5-bo'lim)

### BE-1501 · Kategoriyalar · P0
- Tizim kategoriyalari seed (10 ta: groceries, food, transport, bills, health, shopping, housing, subs, salary, transfer) — id, nom (lokalizatsiya), ikon, rang, tur.
- `GET /v1/categories` → tizim + user kategoriyalari, har birida `type`, `monthly_limit`, joriy oy `spent`.
- `POST /v1/categories` → `{ name, icon, color, type: expense | income, monthly_limit? }` — ikon va rang ruxsat etilgan ro'yxatdan.
- `PATCH /v1/categories/{id}` — tizim kategoriyasida faqat `monthly_limit` (va user override nomi) o'zgaradi.
- `DELETE /v1/categories/{id}` — faqat user kategoriyasi; tranzaksiyalari bor bo'lsa `{ reassign_to }` talab qilinadi.
- **Qabul:** bir user'da bir xil nomli ikki kategoriya → `409`.

---

## 16. Language va Currency (`PROFILE_SETTINGS.md` 6–7-bo'lim)

### BE-1601 · Tillar va lokalizatsiya · P1
- Qo'llab-quvvatlanadigan: `en`, `uz-Latn`, `uz-Cyrl`, `ru`, `kk`, `tr`.
- Server matnlari (bildirishnomalar, kategoriya nomlari, AI javoblari, eksport PDF, xato `message`) `Accept-Language` yoki `user.language` bo'yicha.

### BE-1602 · Valyuta kurslari · P1
- `GET /v1/currencies` → `[{ code, symbol, name, rate_to_uzs }]` (UZS, USD, EUR, RUB, KZT, GBP, CNY, TRY).
- Kurs manbai: CBU API (`cbu.uz`), kuniga bir marta yangilash, kesh.
- Asosiy valyuta o'zgarsa: summalar bazada UZS'da qoladi, ko'rsatish uchun javoblarda `display_currency` bo'yicha konvertatsiya (yoki mijozda kurs bilan). Qaror: server tomonda konvertatsiya, `amount` + `amount_display`.

---

## 17. Help & support (`PROFILE_SETTINGS.md` 8-bo'lim)

### BE-1701 · FAQ · P1
- `GET /v1/help/faq?lang=` → `[{ id, question, answer }]`. Admin orqali tahrirlanadi (CMS yoki jadval).
- `GET /v1/help/contacts` → Telegram, telefon, email (dizayndagi qiymatlar, konfiguratsiyadan).

### BE-1702 · Live chat · P2
- Tayyor servis (Intercom / Crisp / Chatwoot) integratsiyasi yoki o'z WebSocket chati. Minimal: user identifikatori bilan chat sessiyasi ochish endpointi `POST /v1/support/session` → `{ token }`.

---

## 18. Holatlar va xatolar (`STATES.md`)

### BE-1801 · Xato kodlari lug'ati · P0
Mijoz har bir UI holatini aniq kod bo'yicha ko'rsatadi:
| UI holati | HTTP | `code` |
|---|---|---|
| Server error | 5xx | `internal_error` |
| Session expired | 401 | `session_expired` |
| Rate limit | 429 | `rate_limited` (+ `retry_after`) |
| Couldn't read the receipt | 422 | `receipt_unreadable` |
| No QR code / qo'llab-quvvatlanmaydi | 422 | `qr_not_supported` |
| Export failed | — | export `status: failed` |
| Bank sync failed | — | account `sync_status: failed` |
| AI mavjud emas | 503 | `ai_unavailable` |
| Validatsiya | 422 | `validation_error` + `fields[]` |
- Hujjatlashtirilgan (OpenAPI), mijoz jamoasiga beriladi.

### BE-1802 · Empty holatlar uchun signal · P0
- Ro'yxat endpointlari bo'sh massiv qaytaradi (`200`), `404` emas.
- `GET /v1/me` → `onboarding: { balance_set, has_transactions, has_goals, has_reminders }` — Get started checklist va empty holatlar shu asosda.

---

## 19. Hujjat va topshirish

### BE-1901 · OpenAPI spetsifikatsiya · P0
- Barcha endpointlar, DTO'lar, xato kodlari. Flutter uchun client generatsiya qilish mumkin bo'lsin.

### BE-1902 · Testlar · P0
- Har bir modul uchun integratsion testlar; `02-backend.md` oxiridagi "Qabul mezonlari" ro'yxati avtomatik test sifatida.
- Yuklama testi: Home, Activity, Stats — 500 RPS'da p95 < 300 ms.

### BE-1903 · Admin panel (minimal) · P2
- Userlarni qidirish (telefon blind index orqali), FAQ tahrirlash, tizim kategoriyalari, bildirishnoma shablonlari, eksport/scan xatolari statistikasi.

---

## Tavsiya etilgan tartib

1. **Sprint 1:** BE-001, 002, 101–104, 201–204, 1301, 1302, 1401, 1402, 1501, 1801, 1901
2. **Sprint 2:** BE-501–505, 301, 1001, 1101–1103, 1201, 1202, 1802
3. **Sprint 3:** BE-401–404, 601, 602, 701, 703, 801
4. **Sprint 4:** BE-901–903, 1104, 1303, 1304, 1403, 1404, 1601, 1602, 1701, 205, 302, 702
5. **Keyin:** BE-003–005, 105, 106, 1105, 1203, 1405, 1702, 1903

## Ochiq savollar

1. Bank integratsiyasi (BE-1405) MVP'ga kiradimi?
2. Valyuta konvertatsiyasi serverdami yoki mijozdami (BE-1602)?
3. OCR va LLM provayderi: tashqi servis yoki o'z modeli (ma'lumotlarni O'zbekistonda saqlash talabi)?
4. Live chat: tayyor servis yoki o'zimiz?
