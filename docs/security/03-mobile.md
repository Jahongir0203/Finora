# Finora — Xavfsizlik TZ: Mobil ilova (iOS / Android)

Versiya 1.0 · 28.09.2026 · Standart: OWASP MASVS 2.0 L2 + R · Stack: Flutter

**MUST** — majburiy, relizdan oldin. **SHOULD** — tavsiya etiladi, 1-chorakda.
Umumiy qism va parametrlar: [01-umumiy.md](./01-umumiy.md)

---

## 1. Qurilmada saqlash

- **MUST** Tokenlar faqat iOS Keychain (`kSecAttrAccessibleWhenUnlockedThisDeviceOnly`) va Android Keystore (StrongBox mavjud bo'lsa) orqali shifrlangan holda saqlanadi.
- **MUST** SharedPreferences / UserDefaults'da shaxsiy yoki moliyaviy ma'lumot yo'q.
- **MUST** Offline kesh (tranzaksiyalar, balans) SQLCipher bilan shifrlangan. Kalit Keystore/Keychain'da.
- **MUST** Tokenlar va kesh iCloud / Google zaxirasiga tushmaydi (`allowBackup=false`, `isExcludedFromBackup`).
- **MUST** Logout va akkaunt o'chirishda barcha tokenlar, kesh, rasmlar va PIN ma'lumotlari o'chiriladi.

## 2. PIN kod

- **MUST** PIN 4 xonali. Oddiy PIN'lar rad etiladi:
  - bir xil raqamlar: `0000`, `1111` … `9999`
  - ketma-ket: `1234`, `2345`, `4321`, `9876` …
  - yil ko'rinishidagi: `19xx`, `20xx`
- **MUST** PIN ochiq saqlanmaydi. PIN'dan Argon2id (yoki PBKDF2, ≥ 310 000 iteratsiya) orqali kalit hosil qilinadi va u Keystore'dagi refresh tokenni ochadi. PIN xeshi alohida saqlanmaydi.
- **MUST** Urinishlar:
  - 3-xatodan keyin 30 soniya kutish;
  - 5-xatodan keyin tokenlar o'chiriladi, serverga xabar yuboriladi, SMS orqali qayta kirish so'raladi;
  - hisoblagich ilovani o'chirib-yoqish bilan nolga tushmaydi (Keystore'da saqlanadi).
- **MUST** PIN klaviaturasi ilovaning o'zida chiziladi, tizim klaviaturasi va autofill ishlatilmaydi.
- **MUST** PIN almashtirish uchun eski PIN yoki biometriya talab qilinadi.

## 3. Biometriya (Face ID / barmoq izi)

- **MUST** Biometriya kriptografik bog'langan: kalit `setUserAuthenticationRequired(true)` (Android, `BIOMETRIC_STRONG`) / `.biometryCurrentSet` (iOS) bilan yaratiladi. Oddiy `true/false` tekshiruv yetarli emas.
- **MUST** Qurilmaga yangi barmoq izi yoki yuz qo'shilsa, kalit bekor bo'ladi va user PIN kiritib biometriyani qayta yoqadi.
- **MUST** Biometriya faqat qo'shimcha usul: PIN har doim zaxira sifatida ishlaydi.

## 4. Avto-qulf

- **MUST** Faollik bo'lmasa qulf: 1 / 3 / 5 daqiqa (standart 1). Profile → Security'da o'zgartiriladi.
- **MUST** Taymer monoton soat (monotonic clock) bilan o'lchanadi, tizim vaqtini o'zgartirib aylanib o'tib bo'lmaydi.
- **MUST** Ilova fonga o'tganda ham o'sha taymer ishlaydi. Qaytganda muddat o'tgan bo'lsa, birinchi kadr qulf ekrani bo'ladi.
- **MUST** Ilovani to'liq yopib ochganda (cold start) har doim PIN so'raladi.
- **MUST** Qulf paytida xotiradagi balans va ro'yxatlar tozalanadi, qulfdan keyin qayta yuklanadi.
- **MUST** Kirish ekranlarida (splash, auth, OTP, PIN yaratish, boshlang'ich balans) taymer ishlamaydi.

## 5. Ekranni himoya qilish

- **MUST** Android: PIN, OTP, balans va karta ekranlarida `FLAG_SECURE`. Skrinshot va ekran yozish bloklanadi.
- **MUST** iOS: app switcher'da blur/logo qatlami. Ekran yozilayotganini aniqlab balansni yashirish.
- **MUST** Push bildirishnomalarda summa va hisob nomi qulflangan ekranda ko'rsatilmaydi (standart: "Yangi bildirishnoma").
- **MUST** Nusxalangan karta / hisob raqami 60 soniyadan keyin clipboard'dan o'chiriladi.

## 6. Tarmoq

- **MUST** Faqat HTTPS. Android `cleartextTrafficPermitted=false`, iOS ATS istisnolarsiz.
- **MUST** Sertifikat pinning (SPKI SHA-256): asosiy va zaxira pin. Pin almashish rejasi reliz jadvaliga kiritiladi.
- **MUST** Foydalanuvchi o'rnatgan CA sertifikatlariga ishonilmaydi.
- **MUST** Ilova ichida API kalitlari yoki maxfiy ma'lumot yo'q. Uchinchi tomon xizmatlari backend orqali proksi qilinadi.

## 7. Qurilma va ilova yaxlitligi

- **MUST** Play Integrity (Android) va App Attest (iOS) tokeni kirish va refresh so'rovlariga qo'shiladi, backend tekshiradi.
- **MUST** Root / jailbreak, emulyator, debugger va Frida aniqlansa: ogohlantirish ko'rsatiladi, biometriya o'chiriladi, hodisa serverga yuboriladi. Ilova butunlay bloklanmaydi (false positive xavfi).
- **MUST** Reliz build: obfuskatsiya (`flutter build --obfuscate --split-debug-info`, R8), debug loglar va dev menyu olib tashlanadi.
- **SHOULD** Qayta paketlanganini aniqlash: imzo sertifikatini ish vaqtida tekshirish.

## 8. Boshqa talablar

- **MUST** OTP avtomatik o'qiladi (Android SMS Retriever / iOS `one-time-code`). SMS o'qish ruxsati so'ralmaydi.
- **MUST** Kamera ruxsati faqat skaner ochilganda so'raladi. Chek rasmi yuklangandan keyin qurilmadan o'chiriladi va galereyaga saqlanmaydi.
- **MUST** Deep link'lar faqat tasdiqlangan App Links / Universal Links. Parametrlar validatsiya qilinadi, deep link orqali qulfni chetlab o'tib bo'lmaydi.
- **MUST** Crash va analytics hisobotlarida shaxsiy ma'lumot, summa va ekran matni yo'q.
- **MUST** WebView ishlatilsa: JavaScript bridge o'chiq, faqat o'z domenimiz.

---

## Qabul mezonlari (mobil)

- [ ] `1234`, `0000`, `1990` PIN sifatida qabul qilinmaydi
- [ ] 3 xato PIN → 30 s kutish; ilovani qayta ochganda hisoblagich saqlanadi
- [ ] 5 xato PIN → tokenlar o'chgan, SMS kirish ekrani
- [ ] Yangi barmoq izi qo'shilgandan keyin biometriya ishlamaydi, PIN so'raladi
- [ ] 1 daqiqa faolsizlik → qulf; tizim vaqtini oldinga surish qulfni chetlab o'tmaydi
- [ ] Cold start → har doim PIN
- [ ] Android: PIN/balans ekranida skrinshot qora chiqadi
- [ ] iOS: app switcher'da balans ko'rinmaydi
- [ ] Proxy (Charles/mitmproxy) bilan trafik ochilmaydi
- [ ] Rootlangan qurilmada ogohlantirish chiqadi, biometriya o'chadi
- [ ] Qurilma fayl tizimida (backup, prefs, cache) token va ochiq summalar topilmaydi
- [ ] Reliz build'da chap dev menyu va "Demo PIN" yozuvi yo'q
