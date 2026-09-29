# Finora API — xato kodlari lug'ati (BE-1801)

Har bir xato javobi: `{ "code", "message", "request_id" }` + kodga qarab qo'shimcha maydonlar.
`message` so'rov tilida (`Accept-Language`, bo'lmasa `user.language`): en, uz-Latn, uz-Cyrl, ru,
kk, tr. **Mijoz UI holatini faqat `code` bo'yicha tanlaydi** — matnni solishtirmang.

| UI holati | HTTP | `code` | Qo'shimcha maydonlar |
|---|---|---|---|
| Server error | 500 | `internal_error` | — |
| Xizmat ishlamayapti (SMS va h.k.) | 503 | `service_unavailable` | — |
| AI mavjud emas (15 s timeout) | 503 | `ai_unavailable` | — |
| Chek o'qish xizmati ulanmagan | 503 | `ocr_unavailable` | — |
| Avtorizatsiya yo'q / noto'g'ri token | 401 | `unauthorized` | — |
| Access token muddati o'tdi → refresh qiling | 401 | `token_expired` | — |
| **Session expired** (refresh ham o'tmadi) | 401 | `session_expired` | — |
| Sessiya bekor qilingan (refresh reuse) | 401 | `session_revoked` | — |
| Qurilma imzosi noto'g'ri | 401 | `invalid_device_signature` | — |
| Resurs yo'q yoki begona | 404 | `not_found` | — |
| **Rate limit** | 429 | `rate_limited` | `retry_after` (+ `Retry-After` sarlavha) |
| OTP bloklandi (5 xato) | 429 | `otp_blocked` | `retry_after` |
| **Wrong code** | 400 | `otp_invalid` | `attempts_left` |
| Kod muddati o'tdi | 400 | `otp_expired` | — |
| Idempotency-Key yo'q | 400 | `idempotency_key_required` | — |
| Idempotency-Key boshqa tana bilan | 409 | `idempotency_conflict` | — |
| **Validatsiya** | 422 | `validation_error` | `fields[]` |
| Goal nomi bo'sh | 422 | `goal_name_required` | `fields: ["name"]` |
| Goal summasi < 100 000 | 422 | `goal_target_min` | `fields: ["target"]` |
| Kategoriya nomi bo'sh | 422 | `category_name_required` | `fields: ["name"]` |
| Kategoriya turi tranzaksiyaga mos emas | 422 | `category_type_mismatch` | `fields` |
| Kategoriyada tranzaksiyalar bor (`reassign_to` kerak) | 409 | `category_in_use` | — |
| Bir xil nomli kategoriya | 409 | `conflict` | — |
| Withdraw > saved | 422 | `insufficient_funds` | — |
| Muzlatilgan hisob | 422 | `account_frozen` | — |
| **Couldn't read the receipt** | 422 | `receipt_unreadable` | — |
| **QR fiskal chek emas** | 422 | `qr_not_supported` | — |
| Fayl rad etildi (antivirus / buzilgan rasm) | 422 | `file_rejected` | — |
| Rasm formati noto'g'ri | 415 | `unsupported_media_type` | — |
| Play Integrity / App Attest o'tmadi | 422 | `attestation_failed` | `fields` |
| So'rov hajmi katta (1 MB / chek 10 MB) | 413 | `payload_too_large` | — |
| Faqat HTTPS | 403 | `https_required` | — |

Holat maydoni orqali (xato emas):

| UI holati | Qayerda |
|---|---|
| **Export failed** | `GET /v1/exports/{id}` → `status: "failed"`, `error_code: "render_failed"` |
| **Bank sync failed** | hozircha yo'q — bank integratsiyasi (BE-1405) ochiq savol |

Bo'sh ro'yxatlar har doim `200` + bo'sh massiv (BE-1802), `404` emas.
