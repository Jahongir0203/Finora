# Finora — Xavfsizlik TZ: Umumiy qism

Versiya 1.0 · 28.09.2026

| | |
|---|---|
| **Mahsulot** | Finora, shaxsiy moliya ilovasi (UZS) |
| **Qamrov** | SMS orqali kirish, PIN, biometriya, avto-qulf, tranzaksiyalar, byudjet, goallar, eslatmalar, chek skaneri, eksport, AI insights |
| **Standartlar** | OWASP ASVS 4.0 L2 (backend), OWASP MASVS 2.0 L2 + R (mobil), OWASP API Top 10 |
| **Belgilar** | **MUST** — majburiy, relizdan oldin. **SHOULD** — tavsiya etiladi, 1-chorakda. |

Bog'liq hujjatlar: [02-backend.md](./02-backend.md), [03-mobile.md](./03-mobile.md)

---

## 1. Tahdidlar modeli

Ilova bankka ulanmaydi va pul o'tkazmaydi. Lekin foydalanuvchining moliyaviy holati, telefon raqami, cheklar va xarajat odatlari saqlanadi.

| Tahdid | Misol | Himoya |
|---|---|---|
| Akkauntni egallash | OTP brute-force, SIM-swap, o'g'irlangan token | Backend 1, 2 · Mobil 2 |
| Boshqa user ma'lumotini o'qish | `/goals/{id}` ni almashtirib ko'rish (IDOR / BOLA) | Backend 3 |
| Qurilmaga jismoniy kirish | Ochiq qoldirilgan telefon, yelka ortidan qarash | Mobil 2–5 |
| Tarmoqda tinglash | Ommaviy Wi-Fi, soxta sertifikat (MITM) | Backend 4 · Mobil 6 |
| Ilovani buzish | Root/jailbreak, Frida, qayta paketlash | Mobil 7 |
| Ma'lumot sizishi | Loglarda telefon raqami, ochiq S3 bucket, zaxira nusxalar | Backend 5, 6, 9 |
| Suiiste'mol | SMS bombing, AI endpointni ortiqcha chaqirish | Backend 1, 4, 8 |

---

## 2. Parametrlar jadvali

Prototipdagi oqim bilan mos qiymatlar. Backend va mobil jamoalar shu qiymatlardan foydalanadi.

| Parametr | Qiymat | Qayerda |
|---|---|---|
| OTP uzunligi / muddati | 6 xona / 120 s | Backend |
| OTP qayta yuborish | 60 s, soatiga 5 | Backend + mobil taymer |
| OTP urinishlari | 5, keyin 15 daqiqa blok | Backend |
| Access / refresh token | 15 daqiqa / 30 kun, rotation | Backend |
| PIN uzunligi | 4 xona, oddiy PIN'lar taqiqlangan | Mobil |
| PIN urinishlari | 3 → 30 s kutish, 5 → chiqish + SMS | Mobil + backend |
| Avto-qulf | 1 / 3 / 5 daqiqa, standart 1 | Mobil |
| Imzolangan URL (chek) | 5 daqiqa | Backend |
| Eksport fayli | 24 soat, bir martalik havola | Backend |
| Clipboard tozalash | 60 s | Mobil |

---

## 3. Kirish oqimi

```
Splash → Onboarding → Telefon raqami → SMS OTP (6 xona)
       → PIN yaratish (4 xona + tasdiqlash)
       → Boshlang'ich balans (ixtiyoriy, "Skip")
       → Home

Keyingi ochilishlar:
Cold start ─────────────┐
Fonda > avto-qulf vaqti ─┼→ PIN / Face ID → oxirgi ekran
Faolsizlik 1/3/5 min ────┘
5 xato PIN yoki "Forgot PIN?" → SMS OTP → yangi PIN
```

---

## 4. Tekshirish va qabul qilish

- **MUST** Har bir PR: SAST, SCA, secret-scan. Yashil bo'lmasa merge qilinmaydi.
- **MUST** Avtomatik testlar: IDOR (boshqa user ID bilan so'rov → 404), OTP limitlari, refresh reuse, idempotency, withdraw > saved.
- **MUST** Mobil: MASVS L2 checklist bo'yicha ichki tekshiruv (MobSF statik tahlil + qurilmada dinamik test).
- **MUST** Birinchi ommaviy relizdan oldin mustaqil pentest (backend + ikkala platforma). Critical/High topilmalar yopilmaguncha reliz yo'q.
- **MUST** Hodisaga javob rejasi: kim javobgar, aloqa kanali, 24 soat ichida zarar ko'rgan userlarni xabardor qilish, tokenlarni ommaviy bekor qilish tartibi.
- **SHOULD** Relizdan keyin bug bounty yoki mas'uliyatli oshkor qilish sahifasi (`security.txt`).

---

## 5. Huquqiy talablar

- **MUST** O'zbekiston fuqarolarining shaxsiy ma'lumotlari O'zbekiston hududidagi serverlarda saqlanadi ("Shaxsga doir ma'lumotlar to'g'risida"gi qonun). Hosting tanlashdan oldin yurist bilan tasdiqlash.
- **MUST** Maxfiylik siyosati va foydalanish shartlari ilovada va do'kon sahifasida.
- **MUST** Akkauntni o'chirish funksiyasi ilova ichida (App Store va Google Play talabi).

---

> **Prototipga oid eslatma.** Prototipdagi "Demo PIN: 1234" yozuvi, chap navigatsiya menyusi va demo ma'lumotlar production build'ga kirmasligi kerak. Mobil 2-bandga ko'ra 1234 PIN sifatida qabul qilinmaydi.
