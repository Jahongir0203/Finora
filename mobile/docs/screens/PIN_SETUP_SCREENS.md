# Finora — Create PIN, PIN lock, Starting balance

Versiya 1.0 · 28.09.2026 · Flutter (iOS / Android)

3 ta ekranning to'liq UI spetsifikatsiyasi. Skrinshotlar bilan birga AI yoki dasturchiga Flutter kodini yozish uchun beriladi.

Bog'liq hujjatlar:
- `docs/DESIGN_SYSTEM.md` — tokenlar (`AppColors`, `AppTextStyles`, `AppSpacing`, `AppRadius`, `AppMotion`)
- `docs/screens/AUTH_SCREENS.md` — Splash, Onboarding, Sign in, Verify code (umumiy qoidalar 1-bo'limda)
- `docs/screens/HOME_NOTIFICATIONS.md` — Home, yangi foydalanuvchi holati, Notifications
- `docs/security/03-mobile.md` — PIN saqlash, urinishlar limiti, auto-lock talablari

---

## 0. AI uchun ko'rsatma (prompt)

> Quyidagi spetsifikatsiya va skrinshotlar asosida Flutter kodini yoz.
> - Faqat `DESIGN_SYSTEM.md` tokenlaridan foydalan. Rang va o'lchamlarni qattiq yozma.
> - Fayllar: `create_pin_screen.dart`, `pin_lock_screen.dart`, `starting_balance_screen.dart`. Umumiy vidjetlar: `pin_dots.dart`, `pin_keypad.dart`.
> - Riverpod, `go_router`, `lucide_icons`, Onest shrifti.
> - PIN hech qachon ochiq holda saqlanmaydi: `flutter_secure_storage` + hash (`03-mobile.md`).
> - Biometrika: `local_auth`. Haptic: har bosishda `HapticFeedback.selectionClick()`, xatoda `HapticFeedback.heavyImpact()`.
> - Matnlarni o'zgartirma, `.arb` orqali lokalizatsiyaga tayyor qil.
> - Press effekti `scale 0.96`, 120ms. Keypad tugmasi `scale 0.94`. Minimal bosish maydoni 44×44.

---

## 1. Oqim (yangi foydalanuvchi)

```
Splash → Onboarding → Sign in → Verify code (6 raqam)
   → Create PIN (yangi) → Create PIN (takrorlash)
   → Starting balance (ixtiyoriy, "Skip" mumkin)
   → Home (yangi foydalanuvchi holati, "Get started" checklist)
```

Keyingi ochilishlar: `Splash → PIN lock → Home` (yoki oxirgi ochiq ekran).

| Route | Ekran | Qachon |
|---|---|---|
| `/pin/create` | Create PIN | OTP muvaffaqiyatli, PIN hali yo'q |
| `/pin/change` | Create PIN (change rejimi) | Profile → Security → Change PIN |
| `/lock` | PIN lock | Ilova ochilganda, auto-lock, "Lock now" |
| `/setup/balance` | Starting balance | PIN yaratilgandan keyin, bir marta |

---

## 2. Umumiy PIN vidjetlari

Create PIN va PIN lock bir xil fon, nuqtalar va klaviaturadan foydalanadi.

| Parametr | Qiymat |
|---|---|
| Fon | `primary900` `#064E3B` |
| Status bar | oq ikonkalar (`Brightness.light`) |
| Padding | Create PIN: `8 24 36 24` · PIN lock: `24 24 36 24` |
| Vertikal gap | 28 |

### PinDots (4 ta nuqta)

`Row`, markazda, gap 18.

| Holat | Fon | Chegara (2px) | Scale |
|---|---|---|---|
| Bo'sh | transparent | `rgba(167,243,208,0.5)` | 1.0 |
| To'ldirilgan | `primary500` | `primary500` | 1.15 |
| Xato | `danger` `#DC2626` | `danger` | 1.0 |

- O'lcham 16×16, doira.
- O'tish: transform 180ms `Cubic(0.2,0.8,0.2,1)`, fon 150ms.
- Xatoda butun qator **shake**: X `0 → −8 → 7 → −5 → 3 → 0`, 450ms.

### PinKeypad

`GridView` 3 ustun, gap vertikal 10 / gorizontal 18, yon padding 12.

```
1 2 3
4 5 6
7 8 9
[face] 0 [del]
```

| Element | Spetsifikatsiya |
|---|---|
| Tugma | balandlik 68, doira, fon transparent |
| Raqam | 28px Medium (500), oq |
| Pressed | fon `rgba(255,255,255,0.16)`, scale 0.94 |
| `del` | Lucide `delete` 26px, oq |
| `face` | Lucide `scan-face` 28px, `primary200`. Faqat PIN lock'da va biometrika yoqilgan bo'lsa. Aks holda bo'sh katak |

### Kiritish logikasi

- 4 ta raqam kiritilgach, **220ms** kutib tekshiriladi (oxirgi nuqta ko'rinib qolishi uchun).
- 4 ta to'lganda yangi raqam qabul qilinmaydi; `del` ishlaydi.

---

## 3. Create PIN

**Route:** `/pin/create`, `/pin/change` · **Fayl:** `create_pin_screen.dart`

### Tuzilish

```
Scaffold (bg: primary900)
└─ SafeArea → Column (gap 28)
   ├─ TopBar (h 44) — faqat back tugma (shartli)
   ├─ Header (Column, markazda, gap 14)
   │  ├─ IconBadge 64×64
   │  ├─ Title
   │  └─ Subtitle (minHeight 44)
   ├─ PinDots
   ├─ Spacer
   └─ PinKeypad (face yo'q)
```

### Elementlar

| Element | Spetsifikatsiya |
|---|---|
| Back tugma | 44×44 doira, fon `rgba(255,255,255,0.08)`, Lucide `chevron-left` 20 oq |
| IconBadge | 64×64, radius 20, fon `primary500`, ikonka 30px `onPrimary` |
| Title | 26/32 Bold, letterSpacing −0.52, oq |
| Subtitle | 15/22 Regular, maxWidth 280, markazda |

### Bosqichlar

| Bosqich | Ikonka | Title | Subtitle | Rang |
|---|---|---|---|---|
| `new` (setup) | `lock-keyhole` | Create a 4-digit PIN | You'll use it to open Finora. Avoid easy ones like 1234. | `primary200` |
| `new` (change) | `lock-keyhole` | Enter a new PIN | (xuddi shu) | `primary200` |
| `confirm` | `shield-check` | Repeat your PIN | Enter the same PIN once more to confirm. | `primary200` |
| mos kelmadi | `lock-keyhole` | Create a 4-digit PIN | PINs didn't match. Try again. | `#FCA5A5` |

### Xatti-harakat

- `new` → 4 raqam → `confirm` bosqichiga o'tadi, nuqtalar tozalanadi.
- `confirm` mos kelsa:
  - setup → PIN saqlanadi → `/setup/balance`, toast **"PIN created"**
  - change → `/profile`, toast **"PIN changed"**
- Mos kelmasa: shake + xato nuqtalar, `new` bosqichiga qaytadi, mismatch matni ko'rinadi. Birinchi raqam bosilganda xato matni yo'qoladi.
- Back tugma ko'rinadi: `confirm` bosqichida (→ `new`ga qaytadi) yoki change rejimida (→ Profile).
- Setup rejimida Android back: ilovadan chiqmaydi, `confirm` → `new`.
- Tavsiya (backend/mobile): `1234`, `0000`, `1111` kabi oddiy PINlarni rad etish — `03-mobile.md`.

### Animatsiyalar

| Element | Animatsiya | Davomiylik |
|---|---|---|
| Ekran kirishi | push: X +32 → 0, opacity 0 → 1 | 420ms |
| IconBadge | pop: scale 0.6 → 1.06 → 1 | 500ms |
| Bosqich almashishi | Title/ikonka `AnimatedSwitcher` fade | 200ms |

---

## 4. PIN lock

**Route:** `/lock` · **Fayl:** `pin_lock_screen.dart`

### Tuzilish

```
Scaffold (bg: primary900)
└─ SafeArea → Column (gap 28)
   ├─ Header (Column, markazda, gap 12, paddingTop 28)
   │  ├─ Avatar 72×72
   │  ├─ "Welcome back, Doston"
   │  └─ StatusMessage (minHeight 22)
   ├─ AutoLockChip (shartli)
   ├─ PinDots
   ├─ Spacer
   ├─ PinKeypad (face bilan)
   └─ Footer Row (spaceBetween, padding 0 8)
      └─ "Forgot PIN?"
```

### Elementlar

| Element | Spetsifikatsiya |
|---|---|
| Avatar | 72×72 doira, fon `rgba(167,243,208,0.16)`, initsiallar "DK" 24 Bold `primary200` |
| Salom | "Welcome back, {firstName}", 22 Bold, oq |
| StatusMessage | 15 Regular, markazda |
| AutoLockChip | h 32, padding 0 12, radius full, fon `rgba(255,255,255,0.08)`. Lucide `timer` 14 `primary200` + "Locked after {n} min of inactivity" 13px `#D1FAE5`, gap 8 |
| "Forgot PIN?" | h 40, 15 SemiBold, `primary200` |

> Prototipdagi "Demo PIN: 1234" yozuvi faqat demo uchun. Production'da **qo'shilmaydi**.

### StatusMessage holatlari

| Holat | Matn | Rang |
|---|---|---|
| Oddiy | Enter your PIN to continue | `primary200` |
| Face ID skaner | Scanning face… | `primary200` |
| Noto'g'ri PIN | Wrong PIN. {5 − n} attempts left | `#FCA5A5` |

### Xatti-harakat

- **To'g'ri PIN** → `lockFrom` ekraniga qaytadi (auto-lock'dan oldingi ekran). Agar oldingi ekran auth/setup ekranlaridan biri bo'lsa → `/home`. Urinishlar hisoblagichi 0 ga tushadi.
- **Noto'g'ri PIN** → shake, nuqtalar qizil (keyingi raqam bosilguncha), hisoblagich +1.
- **5-urinish** → sessiya tugaydi, `/sign-in`ga o'tadi, toast **"Too many attempts. Sign in again"**. Keyin SMS orqali qayta kirish va yangi PIN.
- **Face ID** (`scan-face`) → `local_auth.authenticate()`, "Scanning face…". Muvaffaqiyatli → ochiladi. Ekran ochilganda biometrika yoqilgan bo'lsa avtomatik bir marta chaqiriladi.
- **Forgot PIN?** → `/sign-in`, toast **"Verify your phone to reset PIN"**. SMS'dan keyin `/pin/create`.
- Android back: ilovani fonga yuboradi, lock'ni yopmaydi.
- Lock ekranida bottom navigatsiya, toast'dan boshqa overlay'lar ko'rinmaydi.

### Auto-lock

| Parametr | Qiymat |
|---|---|
| Sozlama | Profile → Security → Auto-lock: **1 / 3 / 5 min** (default 1 min) |
| Faollik | har qanday `pointerdown`, `keydown`, scroll taymerni yangilaydi |
| Fon | ilova fonga o'tib, belgilangan vaqtdan keyin qaytsa → lock |
| Chip | faqat auto-lock bo'lganda ko'rinadi (ilova ochilganda yoki "Lock now"da yo'q) |
| Istisno | Splash, Onboarding, Sign in, Verify code, Create PIN, Lock, Starting balance ekranlarida auto-lock ishlamaydi |

Tavsiya: `WidgetsBindingObserver.didChangeAppLifecycleState` + `Listener` (root'da) orqali oxirgi faollik vaqti.

### Animatsiyalar

| Element | Animatsiya | Davomiylik |
|---|---|---|
| Ekran | fade 0 → 1 | 350ms |
| Avatar | pop | 500ms |
| AutoLockChip | fade + Y +14 → 0 | 400ms |
| Xato | shake | 450ms |

---

## 5. Starting balance

**Route:** `/setup/balance` · **Fayl:** `starting_balance_screen.dart`

### Tuzilish

```
Scaffold (bg: surface)
└─ SafeArea → Column (padding 8 24 28 24, gap 24)
   ├─ TopBar (h 44, spaceBetween)
   │  ├─ StepIndicator (3 chiziq)
   │  └─ "Skip"
   ├─ Header (gap 14)
   │  ├─ IconBadge 56×56
   │  ├─ Title
   │  └─ Description
   ├─ AmountField + QuickChips (gap 8)
   ├─ "Where do you keep it?" + LocationGrid (gap 8)
   ├─ PrivacyNote
   ├─ Spacer
   └─ Actions (gap 8)
      ├─ "Continue" (primary)
      └─ "I'll do it later" (text)
```

### Elementlar

| Element | Spetsifikatsiya |
|---|---|
| StepIndicator | 3 ta 22×4 chiziq, radius full, gap 6, hammasi `primary500` (oxirgi qadam) |
| "Skip" | h 40, 15 SemiBold, `textSecondary` |
| IconBadge | 56×56, radius 18, fon `primary50` `#ECFDF5`, Lucide `wallet` 26 `primary700` |
| Title | "How much money do you have right now?" 28/34 Bold, letterSpacing −0.56 |
| Description | "Enter your current balance so Finora can track it from day one. This is optional, you can add it later." 15/22, `textSecondary` |
| AmountField | h 72, radius 18, chegara 1.5px, padding 0 18. Input 32 Bold, tabular raqamlar, placeholder "0". O'ngda "UZS" 17 SemiBold `textTertiary` |
| QuickChips | 3 ta teng: **+100K**, **+1M**, **+5M**. h 38, radius 12, fon `background`, 14 SemiBold. Bosilganda summaga qo'shiladi |
| Label | "Where do you keep it?" 13 SemiBold `textSecondary` |
| LocationGrid | 3 ustun, gap 8. Har biri h 76, radius 16, ikonka 22 + label 14 SemiBold, gap 6 |
| PrivacyNote | Lucide `lock` 16 + "Only you can see this. Finora doesn't connect to your bank." 13/18 `textTertiary`, gap 10 |
| "Continue" | h 56, radius 16, 16 SemiBold |
| "I'll do it later" | h 48, 15 SemiBold, `textSecondary`, fonsiz |

### LocationGrid variantlari

| id | Label | Ikonka |
|---|---|---|
| `cash` | Cash | `banknote` |
| `card` | Card (default) | `credit-card` |
| `both` | Both | `layers` |

| Holat | Fon | Chegara | Ikonka/matn |
|---|---|---|---|
| Tanlangan | `primary50` | 1.5px `primary500` | `primary700` |
| Tanlanmagan | transparent | 1.5px `border` | `textSecondary` |

### Holatlar

| Holat | AmountField chegarasi | Continue foni | Continue matni |
|---|---|---|---|
| Bo'sh (0) | `border` | `divider` | `textTertiary` (disabled) |
| Summa > 0 | `primary500` | `primary500` | `onPrimary` |

- Input faqat raqam qabul qiladi, maksimal 12 raqam. Ko'rsatish: `12 500 000` (bo'sh joy bilan ajratilgan).
- Klaviatura: `TextInputType.number`, ochilganda kontent yuqoriga suriladi (`resizeToAvoidBottomInset`).

### Xatti-harakat

- **Continue** (summa > 0) → balans va joy saqlanadi → `/home` (yangi foydalanuvchi holati), toast **"Balance saved · Welcome to Finora"**. Checklist'da 1-band bajarilgan.
- **Skip** yoki **I'll do it later** → balans 0 → `/home`, toast **"Welcome to Finora"**. Home'da "Add your current balance" tugmasi ko'rinadi.
- Ekran faqat bir marta ko'rsatiladi. Keyin balans Home → "Add your current balance" yoki checklist orqali bottom sheet'da kiritiladi (`HOME_NOTIFICATIONS.md`, 3.4).
- Android back: Create PIN'ga qaytmaydi (PIN allaqachon saqlangan); Skip bilan bir xil.

### Animatsiyalar

| Element | Animatsiya | Davomiylik |
|---|---|---|
| Ekran | push X +32 → 0 | 420ms |
| IconBadge | pop | 600ms |
| AmountField chegarasi, Continue foni | rang o'tishi | 200ms |

---

## 6. Qabul mezonlari

- [ ] PIN ikki marta kiritilmasa saqlanmaydi; mos kelmasa shake + xato matni.
- [ ] PIN `flutter_secure_storage`da hash ko'rinishida; loglarda chiqmaydi.
- [ ] 5 noto'g'ri urinish → sessiya o'chiriladi, Sign in ekrani.
- [ ] Face ID bekor qilinsa, PIN klaviatura ishlashda davom etadi.
- [ ] Auto-lock 1/3/5 min to'g'ri ishlaydi, chip faqat auto-lock'da ko'rinadi.
- [ ] Lock'dan keyin foydalanuvchi oldingi ekranga qaytadi.
- [ ] Starting balance'da summa 0 bo'lsa Continue bosilmaydi.
- [ ] Skip → Home'da balans 0 va "Add your current balance" tugmasi.
- [ ] Barcha ekranlar dark mode'da tokenlar orqali to'g'ri ko'rinadi (PIN ekranlari har doim qorong'u yashil).
