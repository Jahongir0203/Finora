# Finora — Auth ekranlari: Splash, Onboarding, Sign in, Verify code

Versiya 1.0 · 28.09.2026 · Flutter (iOS / Android)

Bu hujjat 4 ta ekranning to'liq UI spetsifikatsiyasi: tuzilish, o'lchamlar, ranglar, matnlar, holatlar va animatsiyalar. Skrinshotlar bilan birga AI yoki dasturchiga Flutter kodini yozish uchun beriladi.

Bog'liq hujjatlar:
- `docs/DESIGN_SYSTEM.md` — tokenlar (`AppColors`, `AppTextStyles`, `AppSpacing`, `AppRadius`, `AppMotion`)
- `docs/security/03-mobile.md` — OTP, PIN va xavfsizlik talablari

---

## 0. AI uchun ko'rsatma (prompt)

> Quyidagi spetsifikatsiya va ilova qilingan skrinshotlar asosida Flutter kodini yoz.
> - Faqat `DESIGN_SYSTEM.md` dagi tokenlardan foydalan. Rang, o'lcham va shriftlarni kodga qattiq yozma.
> - Har bir ekran alohida fayl: `splash_screen.dart`, `onboarding_screen.dart`, `sign_in_screen.dart`, `verify_code_screen.dart`.
> - State management: Riverpod (yoki loyihadagi mavjud yechim). UI va logika ajratilgan bo'lsin.
> - Navigatsiya: `go_router`. Route nomlari 7-bo'limda.
> - Ikonkalar: `lucide_icons` paketi. Shrift: `google_fonts` → Onest (yoki assets'ga qo'shilgan Onest).
> - Matnlarni o'zgartirma, `intl` / `.arb` orqali lokalizatsiyaga tayyor qil.
> - Animatsiyalar 6-bo'limdagi qiymatlar bilan. `MediaQuery.disableAnimations` true bo'lsa, cheksiz animatsiyalarni o'chir.
> - Hamma bosiladigan elementlarda press effekti: `scale 0.96`, 120ms.
> - Minimal bosish maydoni 44×44.

---

## 1. Umumiy

| Parametr | Qiymat |
|---|---|
| Dizayn o'lchami | 390 × 844 (iPhone 14/15), barcha o'lchamlarga moslashadi |
| Shrift | Onest 400 / 500 / 600 / 700 |
| Ikonkalar | Lucide, stroke 2 |
| Asosiy tugma | balandlik 56, radius 16, `primary500` fon, `onPrimary` matn, 16 SemiBold |
| Easing | `Cubic(0.2, 0.8, 0.2, 1)` |
| Safe area | Tepada va pastda `SafeArea`; pastki padding ichida hisoblangan |

### Ishlatiladigan ranglar

| Token | HEX | Qayerda |
|---|---|---|
| `primary900` | `#064E3B` | Splash va Onboarding foni |
| `#0B5E48` | `#0B5E48` | Qorong'u fondagi kartalar, progress track, nofaol nuqta |
| `primary500` | `#10B981` | Logo foni, asosiy tugma, faol nuqta, fokus chegarasi |
| `primary200` | `#A7F3D0` | Qorong'u fondagi ikkinchi darajali matn |
| `onPrimary` | `#052E1F` | `primary500` ustidagi matn va ikonka |
| `surface` | `#FFFFFF` | Sign in va Verify code foni |
| `background` | `#F4F7F5` | Back tugma foni, `+998` prefiks foni, keypad pressed |
| `textPrimary` | `#0E1A14` | Sarlavha, input matni |
| `textSecondary` | `#56655D` | Tavsif, label |
| `textTertiary` | `#8B988F` | Placeholder, huquqiy matn, "or" |
| `border` | `#E4EAE6` | Input, outline tugma, ajratgich |
| `divider` | `#EEF2EF` | Disabled tugma foni |
| `primary700` | `#047857` | Havolalar ("Change", "Terms") |
| `danger` | `#DC2626` | Xato chegarasi va matni |

### Status bar

| Ekran | Fon | Ikonkalar |
|---|---|---|
| Splash, Onboarding | `#064E3B` | oq (`Brightness.light`) |
| Sign in, Verify code | `#FFFFFF` | qora (`Brightness.dark`) |

---

## 2. Splash

**Route:** `/splash` · **Fayl:** `splash_screen.dart`

### Tuzilish

```
Scaffold (bg: primary900)
└─ Stack
   ├─ Center
   │  └─ Column (mainAxisSize: min, gap 22)
   │     ├─ Logo (92×92)
   │     └─ Column (gap 6)
   │        ├─ "Finora"
   │        └─ "Smart money, calm mind"
   └─ Positioned (bottom: 72, markazda)
      └─ LoadingBar (120×4)
```

### Elementlar

| Element | Spetsifikatsiya |
|---|---|
| Logo | 92×92, radius 28, fon `primary500`. Ichida Lucide `wallet` 46px, `onPrimary`. Soya: `0 20 50 rgba(16,185,129,0.35)` |
| "Finora" | 36px Bold, letterSpacing −0.72 (−0.02em), oq |
| "Smart money, calm mind" | 15px Regular, `primary200` |
| LoadingBar track | 120×4, radius full, `#0B5E48`, `clipBehavior: hardEdge` |
| LoadingBar indikator | kenglik 40% (48px), `primary500`, radius full |

### Xatti-harakat

- Ekran ochilganda token va sessiya tekshiriladi (fonda).
- **2200ms** dan keyin (yoki tekshiruv tugagach, qaysi biri keyin bo'lsa):
  - birinchi marta → `/onboarding`
  - onboarding ko'rilgan, sessiya yo'q → `/sign-in`
  - sessiya bor → `/lock` (PIN)
- Butun ekran bosilsa, kutmasdan keyingi ekranga o'tadi.
- Orqaga tugmasi (Android) ilovadan chiqaradi.

### Animatsiyalar

| Element | Animatsiya | Davomiylik | Kechikish |
|---|---|---|---|
| Logo | pop: scale 0.6 → 1.06 → 1.0, opacity 0 → 1 (60% da) | 800ms | 0 |
| Matn bloki | fade + slide up: Y +14 → 0, opacity 0 → 1 | 600ms | 300ms |
| LoadingBar | indikator X: −100% → +260%, cheksiz | 1300ms, `easeInOut` | 0 |

---

## 3. Onboarding

**Route:** `/onboarding` · **Fayl:** `onboarding_screen.dart`

### Tuzilish

```
Scaffold (bg: primary900)
└─ SafeArea
   └─ Padding (top 12, left/right 24, bottom 44)
      └─ Column (gap 24)
         ├─ Header (Row, spaceBetween)
         │  ├─ Row (gap 10): mini logo 36×36 + "Finora"
         │  └─ TextButton "Skip"
         ├─ Expanded → PageView (3 slayd)
         │  └─ Column (gap 24)
         │     ├─ Expanded → Illustration (min 290px balandlik)
         │     └─ Text bloki (min 140px balandlik)
         ├─ PageIndicator (3 nuqta)
         └─ Column (gap 10)
            ├─ PrimaryButton ("Next" / "Get started")
            └─ GhostButton "I already have an account"
```

### Header

| Element | Spetsifikatsiya |
|---|---|
| Mini logo | 36×36, radius 11, `primary500`, `wallet` 18px `onPrimary` |
| "Finora" | 20px Bold, oq |
| "Skip" | 15px Medium, `primary200`, balandlik 40, padding 0 4. Bosilsa → `/sign-in` |

### Slaydlar matni

| # | Sarlavha | Tavsif |
|---|---|---|
| 1 | Take control of every so'm | Track spending, set budgets and save toward your goals, all in one place. |
| 2 | Budgets that keep you on track | Set monthly limits per category. Finora warns you before you overspend. |
| 3 | Never miss a payment | Create reminders for bills, rent and subscriptions and get notified on time. |

- Sarlavha: 32px, height 38/32, Bold, letterSpacing −0.64, oq.
- Tavsif: 16px, height 24/16, Regular, `primary200`.
- Sarlavha va tavsif orasida 12px.

### Illyustratsiyalar

Illyustratsiyalar rasm emas, UI kartalardan yig'ilgan widgetlar. Har bir slaydda 2 ta karta, vertikal markazda, orasida 12px. Kartalar biroz qiyshaygan va sekin "suzadi" (float).

**Slayd 1 — Balans**

| Karta | Spetsifikatsiya |
|---|---|
| A. Balans kartasi | fon `#0B5E48`, radius 24, padding 20, gap 14, `rotate(−3°)`. Ichida: "TOTAL BALANCE" (12 SemiBold, UPPERCASE, letterSpacing 0.72, `primary200`) · "24 850 000" 30 Bold + " UZS" 15 `primary200` · progress bar 8px (track `#064E3B`, to'ldirish 68% `primary500`) |
| B. Jamg'arma kartasi | fon `surface`, radius 20, padding 14×16, gap 12, gorizontal margin 18, `rotate(+2°)`. Ichida: 40×40 ikonka konteyner (radius 12, `#10B981` 12%) + `piggy-bank` 20 `primary700` · "Saved 1 200 000 this month" 14 Medium `textPrimary` |

**Slayd 2 — Byudjet**

| Karta | Spetsifikatsiya |
|---|---|
| A. Byudjetlar kartasi | fon `surface`, radius 24, padding 18, gap 14, `rotate(−2°)`. "September budgets" 15 SemiBold. 3 ta qator (gap 6): nom va foiz (13px, foiz `textSecondary`) + 8px progress (track `divider`): Groceries 74% `primary500` · Transport 77% `warning #F59E0B` · Shopping 52% `primary500` |
| B. Ogohlantirish | fon `dangerSoft #FEF2F2`, radius 18, padding 12×14, gap 10, margin 24, `rotate(+2°)`. `triangle-alert` 18 `danger` + "Food budget is 90% used" 14 Medium |

**Slayd 3 — Eslatmalar**

| Karta | Spetsifikatsiya |
|---|---|
| A. Eslatma | fon `surface`, radius 22, padding 14×16, gap 12, `rotate(−2°)`. 44×44 konteyner (radius 14, `warningSoft #FEF3C7`) ichida `bell-ring` 20 `warningText #B45309` (ring animatsiyasi). Matn: "Electricity due tomorrow" 15 SemiBold · "142 000 UZS · Monthly" 13 `textSecondary` |
| B. Ijara | fon `#0B5E48`, radius 22, padding 14×16, gap 12, margin 16, `rotate(+2°)`. 44×44 sana bloki (radius 14, `#064E3B`): "OCT" 10 SemiBold `primary200` + "05" 16 Bold oq. Matn: "Rent" 15 SemiBold oq · "4 500 000 UZS · in 7 days" 13 `primary200` |

### Page indicator

- 3 ta nuqta, gap 6, balandlik 8, radius full.
- Faol: kenglik **24**, `primary500`. Nofaol: kenglik **8**, `#0B5E48`.
- O'zgarish: kenglik va rang 350ms, asosiy easing.

### Tugmalar

| Tugma | Spetsifikatsiya | Harakat |
|---|---|---|
| Primary | 56px, radius 16, `primary500`, "Next" (1–2 slayd) / "Get started" (3-slayd), 16 SemiBold `onPrimary` | Keyingi slayd; oxirgisida → `/sign-in` |
| Ghost | 48px, radius 16, shaffof, "I already have an account", 15 Medium oq | → `/sign-in` |

### Xatti-harakat

- Chapga/o'ngga swipe bilan slaydlar almashadi (`PageView`).
- Onboarding ko'rilgani `onboarding_seen = true` qilib saqlanadi (Skip yoki Get started bosilganda).
- Android orqaga: 2–3 slaydda oldingi slaydga, 1-slaydda ilovadan chiqish.

### Animatsiyalar

| Element | Animatsiya | Davomiylik |
|---|---|---|
| Ekran kirishi | fade 0 → 1 | 500ms |
| Slayd kirishi | slide X +32 → 0, opacity 0 → 1 | 500ms |
| Kartalar | float: Y 0 → −8 → 0, cheksiz. 2-karta 800ms kechikadi | 4000ms, `easeInOut` |
| Progress barlar | scaleX 0 → 1, chapdan. Slayd 2: 200 / 350 / 500ms kechikish | 1000–1200ms |
| Bell (slayd 3) | ring: 0° → 14° → −12° → 8° → −4° → 0° (siklning 70–90% qismida) | 2400ms, cheksiz |

---

## 4. Sign in (telefon raqami)

**Route:** `/sign-in` · **Fayl:** `sign_in_screen.dart`

### Tuzilish

```
Scaffold (bg: surface, resizeToAvoidBottomInset: true)
└─ SafeArea
   └─ Padding (top 8, left/right 24, bottom 40)
      └─ Column (gap 24)
         ├─ BackButton (44×44)
         ├─ Title bloki (gap 8)
         ├─ Phone field bloki (gap 8)
         ├─ PrimaryButton "Continue"
         ├─ Divider "or"
         ├─ Column (gap 10): Apple, Google
         ├─ Spacer
         └─ Legal text
```

### Elementlar

| Element | Spetsifikatsiya |
|---|---|
| Back tugma | 44×44 doira, fon `background`, `chevron-left` 20 `textPrimary`. → `/onboarding` |
| Sarlavha | "Welcome to Finora" — 28px, height 34/28, Bold, letterSpacing −0.56 |
| Tavsif | "Enter your phone number. We'll send you a 6-digit code." — 15px, height 22/15, `textSecondary` |
| Label | "Phone number" — 13 SemiBold `textSecondary` |
| Phone field | balandlik 56, radius 16, chegara **1.5px** (holatga qarab), `clip` |
| ├ Prefiks | "+998" — 16 SemiBold, padding 0 14, fon `background`, o'ngda 1px `border` ajratgich. O'zgarmaydi |
| └ Input | placeholder "90 123 45 67" (`textTertiary`), 17 Medium, letterSpacing 0.34, padding 0 14, `keyboardType: phone` |
| Continue | 56px, radius 16, 16 SemiBold. Holatlari quyida |
| "or" ajratgich | Row (gap 12): 1px chiziq `border` · "or" 13 `textTertiary` · 1px chiziq |
| Apple / Google | 52px, radius 16, 1px `border`, shaffof fon, 15 SemiBold `textPrimary`. Chapda brend logosi 20px, gap 10 |
| Huquqiy matn | "By continuing you agree to the **Terms** and **Privacy Policy**." — 13px, height 19/13, `textTertiary`, markazda. "Terms" va "Privacy Policy" 13 SemiBold `primary700`, bosiladi (in-app browser) |

### Telefon formati

- Faqat raqamlar, maksimal **9 ta** (prefiks `+998` alohida).
- Ko'rinish maskasi: `XX XXX XX XX` → `90 123 45 67`.
- Paste qilinganda `+998` va bo'sh joylar olib tashlanadi.
- Yuborishda to'liq format: `+998901234567` (E.164).

### Holatlar

| Holat | Chegara | Continue tugma | Qo'shimcha |
|---|---|---|---|
| Bo'sh / to'liq emas | `primary500` 1.5px (fokusda) | fon `divider`, matn `textTertiary` | — |
| 9 raqam kiritilgan | `primary500` 1.5px | fon `primary500`, matn `onPrimary` | — |
| Xato (to'liq emas holda Continue) | `danger` 1.5px + shake | o'zgarmaydi | Ostida: `circle-alert` 15 + "Enter a valid 9-digit phone number" 13 Medium `danger`, fade-in 300ms |
| Yuborilmoqda | — | matn o'rniga 20px oq-yashil spinner, bosib bo'lmaydi | — |
| Server xatosi / limit | — | qaytadi | Toast: "Too many attempts. Try again in N min" |

- Raqam o'zgarsa xato holati darhol yo'qoladi.
- Tugma disabled ko'rinishda ham bosiladi: bosilganda validatsiya xatosini ko'rsatadi.

### Xatti-harakat

- Continue (valid) → `POST /auth/otp` → `/verify` (telefon raqami bilan).
- Apple / Google → native sign-in → muvaffaqiyatli bo'lsa telefonni tasdiqlash so'raladi (keyingi versiya). Prototipda to'g'ridan-to'g'ri Home.
- Klaviatura ochilganda kontent tepaga suriladi, sarlavha ko'rinib turadi.

### Animatsiyalar

| Element | Animatsiya |
|---|---|
| Ekran kirishi | slide X +32 → 0, opacity 0 → 1, 420ms |
| Shake (xato) | X: 0 → −8 → 7 → −5 → 3 → 0, 450ms. Har bosishda qayta ishga tushadi |
| Tugma rangi | 200ms fon o'tishi |

---

## 5. Verify code (SMS OTP)

**Route:** `/verify` · **Fayl:** `verify_code_screen.dart`

### Tuzilish

```
Scaffold (bg: surface)
└─ SafeArea
   └─ Padding (top 8, left/right 24, bottom 24)
      └─ Column (gap 24)
         ├─ BackButton (44×44)
         ├─ Title bloki (gap 8)
         ├─ OtpBoxes (6 ta, grid)
         ├─ Status bloki (gap 4)
         ├─ Spacer
         └─ NumericKeypad (3×4)
```

### Elementlar

| Element | Spetsifikatsiya |
|---|---|
| Back tugma | 44×44 doira, `background`, `chevron-left` 20. → `/sign-in` |
| Sarlavha | "Enter the code" — 28px, height 34/28, Bold, letterSpacing −0.56 |
| Tavsif | "Sent by SMS to **+998 90 123 45 67**. **Change**" — 15px, height 22/15, `textSecondary`. Raqam 600 `textPrimary`. "Change" 15 SemiBold `primary700`, bosilsa → `/sign-in` |
| OTP kataklari | 6 ta, teng kenglik, gap 8, balandlik 58, radius 14. Raqam 24 SemiBold markazda |
| Status | 14 Medium, holatga qarab (quyida) |
| Klaviatura | 3×4 grid, gap 6. Tugma balandligi 56, radius 14, raqam 24 Medium `textPrimary`. Pressed: fon `background`. Tartib: `1 2 3 / 4 5 6 / 7 8 9 / [bo'sh] 0 [delete]`. Delete — Lucide `delete` 22 |

### OTP katak holatlari

| Holat | Chegara (1.5px) |
|---|---|
| Bo'sh | `border` |
| Joriy (keyingi kiritiladigan) | `primary500` |
| To'ldirilgan | `textPrimary` |
| Xato (hammasi) | `danger` |

### Status matni

| Holat | Matn | Rang |
|---|---|---|
| Kutilmoqda | "Resend code in 0:59" (teskari sanoq) | `textSecondary` |
| Sanoq tugadi | "Resend code" (bosiladi, 14 SemiBold) | `primary700` |
| 6 raqam kiritildi | "Verifying…" (+ 14px spinner chapda) | `textSecondary` |
| Noto'g'ri kod | "Incorrect code. N attempts left." | `danger` |
| Limit | "Too many attempts. Try again in 15 min." | `danger` |

### Xatti-harakat

- Ekran ochilishi bilan 60 soniyalik teskari sanoq boshlanadi.
- SMS avtomatik o'qiladi: Android SMS Retriever / iOS `AutofillHints.oneTimeCode`. Kod kelsa kataklarga o'zi yoziladi.
- 6-raqam kiritilgach **200ms** kutib `POST /auth/verify` yuboriladi. Qo'lda tasdiqlash tugmasi yo'q.
- Kod to'g'ri:
  - yangi user → `/pin/create`
  - mavjud user, yangi qurilma → `/pin/create`
  - mavjud user, PIN bor → `/home`
- Kod noto'g'ri: kataklar qizil + shake, 600ms dan keyin tozalanadi, holat "Kutilmoqda"ga qaytadi (xato matni qoladi).
- 5 xato → limit holati, klaviatura bloklanadi.
- "Resend code" → yangi SMS, sanoq qaytadan 60 s, eski kod bekor.
- Delete bosilsa oxirgi raqam o'chadi; uzoq bosilsa hammasi o'chadi.
- Klaviatura ilovaning o'zida chiziladi (tizim klaviaturasi ochilmaydi).

### Animatsiyalar

| Element | Animatsiya |
|---|---|
| Ekran kirishi | slide X +32 → 0, opacity 0 → 1, 420ms |
| Raqam kiritilishi | katakdagi raqam scale 0.6 → 1, 150ms |
| Joriy katak chegarasi | rang o'tishi 150ms |
| Xato | shake 450ms (butun qator) |
| Tugma bosilishi | fon `background`, 100ms |

---

## 6. Animatsiya tokenlari (qisqacha)

| Nomi | Qiymat |
|---|---|
| `AppMotion.ease` | `Cubic(0.2, 0.8, 0.2, 1)` |
| Ekran push | 420ms, X +32 → 0, fade |
| Ekran fade | 500ms |
| Pop | 800ms, scale 0.6 → 1.06 → 1 |
| Float | 4000ms, Y 0 ↔ −8, `easeInOut`, cheksiz |
| Shake | 450ms, X [0, −8, 7, −5, 3, 0] |
| Press | scale 0.96, 120ms |
| Loading bar | 1300ms, X −100% → 260%, cheksiz |

---

## 7. Navigatsiya

```
/splash ──(2.2s)──┬─ birinchi marta ─────────→ /onboarding ──→ /sign-in
                  ├─ sessiya yo'q ───────────→ /sign-in
                  └─ sessiya bor ────────────→ /lock

/sign-in ──Continue──→ /verify ──kod to'g'ri──┬─ PIN yo'q → /pin/create → /setup/balance → /home
                                               └─ PIN bor ─→ /home
```

| Route | Ekran | Orqaga |
|---|---|---|
| `/splash` | Splash | ilovadan chiqish |
| `/onboarding` | Onboarding | oldingi slayd / chiqish |
| `/sign-in` | Sign in | `/onboarding` |
| `/verify` | Verify code | `/sign-in` |

---

## 8. Qabul mezonlari

- [ ] Splash 2.2 s dan keyin to'g'ri ekranga o'tadi, bosilsa darhol o'tadi
- [ ] Onboarding swipe va "Next" bilan ishlaydi, nuqtalar animatsiya bilan almashadi
- [ ] "Skip" va "I already have an account" → Sign in, onboarding qayta ko'rsatilmaydi
- [ ] Telefon maskasi `90 123 45 67`, 9 raqamdan ortiq kiritilmaydi, paste ishlaydi
- [ ] To'liq bo'lmagan raqam bilan Continue → qizil chegara, shake va xato matni
- [ ] Verify'da 60 s teskari sanoq, keyin "Resend code"
- [ ] SMS kod avtomatik to'ladi (Android va iOS)
- [ ] Noto'g'ri kod → qizil kataklar va shake, qolgan urinishlar soni
- [ ] Status bar ranglari ekranlarga mos
- [ ] 320px kenglikda (iPhone SE) hech narsa kesilmaydi va sig'adi
- [ ] Dark mode'da Sign in / Verify `surface` va matn ranglari dark tokenlarga o'tadi

---

## 9. Prototipdan farqlar (production uchun)

| Prototipda | Production'da |
|---|---|
| "Demo code: 123456" yozuvi | Olib tashlanadi |
| "Resend code in 0:42" statik | Haqiqiy 60 s teskari sanoq |
| "2 attempts left" statik | Serverdan kelgan qolgan urinishlar soni |
| Apple / Google tugmalari logosiz | Brend logolari (Apple, Google qoidalariga mos) |
| Social sign-in → Home | Native sign-in + telefonni tasdiqlash |
| Splash bosilganda Onboarding | Sessiyaga qarab yo'naltirish (7-bo'lim) |
