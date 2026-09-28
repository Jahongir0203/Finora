# Finora — Xavfsizlik TZ: Backend

Versiya 1.0 · 28.09.2026 · Standart: OWASP ASVS 4.0 L2, OWASP API Top 10

**MUST** — majburiy, relizdan oldin. **SHOULD** — tavsiya etiladi, 1-chorakda.
Umumiy qism va parametrlar: [01-umumiy.md](./01-umumiy.md)

---

## 1. SMS orqali kirish (OTP)

- **MUST** OTP 6 xonali, kriptografik tasodifiy generator (CSPRNG) bilan yaratiladi.
- **MUST** Amal qilish muddati 120 soniya. Bitta kod faqat bir marta ishlatiladi.
- **MUST** Bazada kodning o'zi emas, HMAC-SHA256 xeshi saqlanadi. Taqqoslash doimiy vaqtda (constant-time) bajariladi.
- **MUST** Bitta kodga 5 ta urinish. 5-xatodan keyin kod bekor qilinadi va raqam 15 daqiqaga bloklanadi.
- **MUST** Qayta yuborish 60 soniyadan keyin, soatiga ko'pi bilan 5 ta SMS. Limit raqam, IP va qurilma bo'yicha alohida hisoblanadi (4-bo'lim jadvali).
- **MUST** Javob raqam ro'yxatdan o'tgan yoki o'tmaganini oshkor qilmaydi: har doim bir xil "Kod yuborildi" javobi.
- **SHOULD** SMS provayderi SIM-swap ma'lumotini bersa, oxirgi 72 soatda SIM almashgan raqam uchun qo'shimcha tasdiqlash so'raladi.
- **SHOULD** SMS so'rashdan oldin Play Integrity / App Attest tokeni tekshiriladi.

## 2. Tokenlar va sessiyalar

- **MUST** Access token 15 daqiqa, imzo ES256 yoki EdDSA. Payloadda faqat `sub`, `sid`, `did`, `exp` bo'ladi, shaxsiy ma'lumot yo'q.
- **MUST** Refresh token opaque (256 bit), bazada xesh ko'rinishida, 30 kun. Har foydalanishda almashtiriladi (rotation).
- **MUST** Eski refresh token qayta ishlatilsa (reuse), shu sessiya oilasidagi barcha tokenlar bekor qilinadi va user "New sign-in" bildirishnomasini oladi.
- **MUST** Refresh token qurilmaga bog'lanadi: qurilma birinchi kirishda ochiq kalit (public key) yuboradi, refresh so'rovi shu kalit bilan imzolanadi.
- **MUST** Profil ichida faol qurilmalar ro'yxati va "Barcha qurilmalardan chiqish" funksiyasi.
- **MUST** Yangi qurilmadan kirilganda eski qurilmalarga push va ilova ichida bildirishnoma yuboriladi.
- **MUST** Logout serverda refresh tokenni bekor qiladi, faqat mijozda o'chirish yetarli emas.

## 3. Avtorizatsiya

- **MUST** Har bir so'rovda resurs egasi tekshiriladi: `WHERE id = :id AND user_id = :sub`. Tekshiruv repository qatlamida majburiy qilinadi, controllerga qoldirilmaydi.
- **MUST** Tashqi ID'lar UUIDv7, ketma-ket raqamlar ishlatilmaydi.
- **MUST** Begona resursga so'rov 404 qaytaradi (403 emas), mavjudlik oshkor bo'lmasligi uchun.
- **MUST** Mass assignment taqiqlanadi: DTO'da faqat ruxsat etilgan maydonlar. `user_id`, `saved` kabi maydonlar mijozdan qabul qilinmaydi.
- **MUST** Goal balansi (`saved`) faqat deposit/withdraw yozuvlaridan serverda hisoblanadi. Withdraw summasi mavjud qoldiqdan oshmasligi serverda tekshiriladi.

## 4. API va tarmoq

- **MUST** Faqat TLS 1.2+ (1.3 afzal), HSTS `max-age=31536000; includeSubDomains`. HTTP so'rovlar rad etiladi.
- **MUST** Barcha kirishlar sxema bo'yicha validatsiya qilinadi. Summa butun son (so'm), `0 < x ≤ 10^12`. Matn maydonlari uzunligi cheklanadi (nom ≤ 64 belgi).
- **MUST** Yozuv yaratuvchi so'rovlar (tranzaksiya, deposit, withdraw) `Idempotency-Key` sarlavhasini talab qiladi, kalit 24 soat saqlanadi.
- **MUST** Xato javoblarida stack trace, SQL yoki ichki yo'llar ko'rsatilmaydi. Yagona format: `{ code, message, request_id }`.
- **MUST** So'rov tanasi ≤ 1 MB. Chek rasmi uchun alohida endpoint, ≤ 10 MB.
- **SHOULD** WAF va DDoS himoyasi (L7 rate limit) API gateway darajasida.

### Rate limit jadvali

| Endpoint | Limit | Kalit |
|---|---|---|
| `POST /auth/otp` | 1 / 60 s, 5 / soat, 10 / kun | telefon + IP + qurilma |
| `POST /auth/verify` | 5 / kod, 20 / soat | telefon + IP |
| `POST /auth/refresh` | 30 / soat | sessiya |
| `POST /receipts/scan` | 30 / soat | user |
| `POST /ai/ask` | 20 / soat, 100 / kun | user |
| `POST /exports` | 10 / soat | user |
| Boshqa (autentifikatsiyalangan) | 300 / daqiqa | user |

Limitdan oshganda `429` va `Retry-After` sarlavhasi qaytariladi.

## 5. Ma'lumotlarni saqlash

- **MUST** Disk va zaxira nusxalar AES-256 bilan shifrlanadi. Kalitlar KMS/HSM'da, har yili almashtiriladi.
- **MUST** Telefon raqami alohida shifrlanadi (field-level). Qidiruv uchun HMAC "blind index" ishlatiladi.
- **MUST** O'zbekiston fuqarolarining shaxsiy ma'lumotlari O'zbekiston hududidagi serverlarda saqlanadi.
- **MUST** Akkauntni o'chirish: so'rovdan keyin 30 kun ichida barcha shaxsiy ma'lumot, cheklar va eksportlar o'chiriladi. Zaxiralardan navbatdagi aylanishda.
- **MUST** Baza foydalanuvchilari minimal huquqli: ilova xizmati `DROP` / `ALTER` qila olmaydi. Faqat parametrli so'rovlar ishlatiladi.

## 6. Fayllar: cheklar va eksport

- **MUST** Chek rasmlari yopiq bucket'da. Ochish faqat 5 daqiqalik imzolangan URL orqali.
- **MUST** Yuklashda MIME magic-bytes bo'yicha tekshiriladi (JPEG/PNG/HEIC), EXIF va GPS olib tashlanadi, antivirus skanidan o'tkaziladi.
- **MUST** CSV/Excel eksportda `=` `+` `-` `@` bilan boshlanuvchi hujayralar oldiga `'` qo'yiladi (formula injection).
- **MUST** Tayyor eksport fayli 24 soatdan keyin o'chiriladi. Yuklab olish havolasi bir martalik.

## 7. PIN va biometriya (server tomoni)

- **MUST** PIN serverga yuborilmaydi va serverda saqlanmaydi. PIN faqat qurilmadagi kalitni ochadi ([03-mobile.md](./03-mobile.md), 2-bo'lim).
- **MUST** "Forgot PIN?" qayta SMS OTP'dan o'tishni talab qiladi va eski qurilma sessiyasini bekor qiladi.
- **MUST** Mijoz 5 marta xato PIN haqida xabar bersa, server shu qurilma sessiyasini bekor qiladi (so'rov qurilma kaliti bilan imzolangan bo'lishi shart).

## 8. AI insights

- **MUST** Modelga faqat kategoriya bo'yicha jamlangan summalar yuboriladi. Ism, telefon, karta raqami, chek rasmi yuborilmaydi.
- **MUST** Model javobi oddiy matn sifatida qaytariladi. Havolalar, HTML va amallar (tool calls) bajarilmaydi.
- **MUST** Provayder bilan shartnomada ma'lumotni o'qitishda ishlatmaslik sharti bo'lishi.

## 9. Loglar, monitoring, infratuzilma

- **MUST** Loglarda token, OTP, to'liq telefon raqami (faqat `+998 90 *** ** 67`), summalar va chek matni bo'lmaydi.
- **MUST** Audit log: kirish, yangi qurilma, logout, PIN reset, akkaunt o'chirish, eksport. O'zgartirib bo'lmaydigan saqlash, 1 yil.
- **MUST** Alertlar: OTP xatolari keskin oshsa, refresh reuse bo'lsa, bitta IP'dan ko'p raqam kelsa.
- **MUST** Secrets Vault / KMS'da. Repo va CI loglarida hech qanday kalit yo'q. Git'da secret-scanning yoqilgan.
- **MUST** CI'da SAST, bog'liqliklar skaneri (SCA) va konteyner skaneri. Critical/High zaifliklar bilan reliz qilinmaydi.
- **SHOULD** Prod muhitiga kirish faqat VPN + MFA orqali, har bir kirish loglanadi.

---

## Qabul mezonlari (backend)

- [ ] Boshqa user resursiga so'rov → `404` (goals, transactions, reminders, receipts, exports)
- [ ] 6-OTP urinishi → `429`, raqam 15 daqiqa bloklangan
- [ ] 61 soniyadan oldin qayta SMS → `429`
- [ ] Ishlatilgan refresh token qayta yuborilsa → barcha sessiya tokenlari bekor
- [ ] Bir xil `Idempotency-Key` bilan 2 ta deposit → bitta yozuv
- [ ] Withdraw > saved → `422`
- [ ] Loglarda to'liq telefon raqami va OTP topilmaydi
- [ ] CSV eksportda `=cmd` qiymati `'=cmd` bo'lib chiqadi
