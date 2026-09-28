# Finora Design System

Versiya 1.0 · 28.09.2026 · Platforma: Flutter (iOS / Android)

Finora — shaxsiy moliya ilovasi. Asosiy rang yashil `#10B981`, shrift Onest, ikonkalar Lucide, valyuta UZS. Interfeys tili ingliz tili.

Manbalar: `Finora Design System.dc.html` (vizual), `Finora App.dc.html` (prototip).

---

## Mundarija

1. [Asosiy tamoyillar](#1-asosiy-tamoyillar)
2. [Ranglar](#2-ranglar)
3. [Tipografiya](#3-tipografiya)
4. [Ikonkalar](#4-ikonkalar)
5. [Spacing, radius, soyalar](#5-spacing-radius-soyalar)
6. [Komponentlar](#6-komponentlar)
7. [Ekran shablonlari](#7-ekran-shablonlari)
8. [Holatlar: bo'sh, xato, yuklanish](#8-holatlar-bosh-xato-yuklanish)
9. [Animatsiya](#9-animatsiya)
10. [Dark mode](#10-dark-mode)
11. [Raqamlar va matn formatlash](#11-raqamlar-va-matn-formatlash)
12. [Accessibility](#12-accessibility)
13. [Flutter kodi](#13-flutter-kodi)

---

## 1. Asosiy tamoyillar

- **Pul birinchi.** Balans va summalar eng katta va eng qalin element. Raqamlar har doim `tabular-nums`.
- **Bitta asosiy harakat.** Har bir ekranda bitta yashil (primary500) tugma. Qolganlari secondary yoki outline.
- **Yumshoq yuzalar.** Oq kartalar och kulrang-yashil fon ustida, 1px chegara, soyasiz.
- **Qorong'u yashil — muhim joylar uchun.** `primary900` faqat balans kartasi, goal hero kartasi, PIN va onboarding ekranlarida.
- **Qizil — faqat muammo uchun.** Limitdan oshish, xato, o'chirish. Xarajatlar qizil emas, oddiy `textPrimary`.

---

## 2. Ranglar

### 2.1 Primary

| Token | HEX | Ishlatilishi |
|---|---|---|
| `primary50` | `#ECFDF5` | Tinted yuzalar, secondary tugma foni |
| `primary100` | `#D1FAE5` | Avatar, yumshoq fon |
| `primary200` | `#A7F3D0` | Qorong'u yashil ustidagi matn |
| `primary300` | `#6EE7B7` | Grafiklar |
| `primary400` | `#34D399` | Grafiklar, hover, unread nuqta |
| `primary500` | `#10B981` | **Brend.** Tugmalar, FAB, faol toggle |
| `primary600` | `#059669` | Pressed holat |
| `primary700` | `#047857` | Matn, daromad summasi, faol tab |
| `primary800` | `#065F46` | Qorong'u yuzalar |
| `primary900` | `#064E3B` | Balans kartasi, PIN/onboarding fon |
| `primary950` | `#052E1F` | Home header fon, `onPrimary` matn |

### 2.2 Neutral

| Token | HEX | Ishlatilishi |
|---|---|---|
| `textPrimary` | `#0E1A14` | Sarlavha, asosiy matn, xarajat summasi |
| `textSecondary` | `#56655D` | Ikkinchi darajali matn |
| `textTertiary` | `#8B988F` | Meta, placeholder, vaqt |
| `textDisabled` | `#C3CDC7` | O'chiq holat |
| `border` | `#E4EAE6` | Karta chegarasi, input |
| `divider` | `#EEF2EF` | Qator ajratgich, progress track |
| `background` | `#F4F7F5` | Ilova foni |
| `surface` | `#FFFFFF` | Karta, bottom sheet |
| `scrim` | `rgba(6,20,14,0.45)` | Sheet orqasidagi qoplama |

### 2.3 Semantic

| Token | HEX | Ishlatilishi |
|---|---|---|
| `success` | `#10B981` | Daromad, "on track" |
| `danger` | `#DC2626` | Limitdan oshish, xato, o'chirish |
| `dangerSoft` | `#FEF2F2` | Xato foni, destructive tugma |
| `warning` | `#F59E0B` | Limitga yaqin (≥ 75%) |
| `warningText` | `#B45309` | Ogohlantirish matni |
| `warningSoft` | `#FEF3C7` | Offline banner foni |
| `info` | `#3B82F6` | Ma'lumot, muzlatilgan karta |
| `onPrimary` | `#052E1F` | `primary500` ustidagi matn va ikonka |

> `primary500` ustida oq matn ishlatilmaydi (kontrast yetarli emas). Har doim `onPrimary`.

### 2.4 Kategoriya ranglari

| Token | HEX | Kategoriya | Ikonka |
|---|---|---|---|
| `catGroceries` | `#10B981` | Groceries | `shopping-cart` |
| `catFood` | `#F59E0B` | Food & drinks | `utensils` |
| `catTransport` | `#3B82F6` | Transport | `car` |
| `catBills` | `#8B5CF6` | Bills | `receipt` |
| `catHealth` | `#EF4444` | Health | `heart-pulse` |
| `catShopping` | `#EC4899` | Shopping | `shopping-bag` |
| `catHousing` | `#14B8A6` | Housing | `house` |
| `catSubs` | `#6366F1` | Subscriptions | `repeat` |
| `catTransfer` | `#0EA5E9` | Transfers | `arrow-left-right` |

Kategoriya ikonkasi foni: shu rang **12% shaffoflikda** (`color + 1F`), ikonka rangi — to'liq rang.

### 2.5 Kartalar (bank kartalari)

| Bank | Fon |
|---|---|
| Kapitalbank Uzcard | `#064E3B` |
| Hamkorbank Humo | `#1E293B` |
| TBC Visa | `#4C1D95` |

---

## 3. Tipografiya

**Shrift:** Onest (Google Fonts), Latin + Cyrillic. O'zbek lotin (`o'`, `g'`) va kirill harflarini qo'llaydi.
**Og'irliklar:** Regular 400 · Medium 500 · SemiBold 600 · Bold 700.

| Token | O'lcham / qator | Og'irlik | Letter-spacing | Misol |
|---|---|---|---|---|
| `displayLarge` | 40 / 48 | 700 | −0.03em | 24 850 000 |
| `display` | 32 / 40 | 700 | −0.02em | 5 460 000 UZS |
| `headline` | 24 / 32 | 700 | −0.01em | Budgets & goals |
| `title` | 20 / 28 | 600 | 0 | Recent transactions |
| `titleSmall` | 17 / 24 | 600 | 0 | September spending |
| `body` | 15 / 22 | 400 | 0 | You spent 12% less on food |
| `bodyMedium` | 15 / 22 | 500 | 0 | Korzinka · Groceries |
| `caption` | 13 / 18 | 400 | 0 | Today, 14:20 |
| `label` | 12 / 16 | 600 | 0.06em, UPPERCASE | TOTAL BALANCE |
| `tabLabel` | 11 / 14 | 500 | 0 | Home |

Qoidalar:
- Summalarda `FontFeature.tabularFigures()`.
- Summa yonidagi `UZS` asosiy raqamdan ~50% kichik, `Medium 500`, ikkinchi darajali rangda.
- Minimal matn o'lchami 11px (faqat tab label).

---

## 4. Ikonkalar

**Kutubxona:** [Lucide](https://lucide.dev) · stroke 1.5–2px · 24px grid.
**O'lchamlar:** 14 (inline), 16 (chip, kichik tugma), 18 (qator oxiri), 20 (list ikonka), 22 (quick action), 24–28 (hero).

| Guruh | Token → Lucide nomi |
|---|---|
| **Navigation** | `home` → house · `activity` → arrow-left-right · `stats` → chart-pie · `budgets` → target · `profile` → user · `back` → chevron-left · `forward` → chevron-right · `close` → x |
| **Actions** | `add` → plus · `send` → send · `scan` → scan-line · `search` → search · `filter` → sliders-horizontal · `notifications` → bell · `show` → eye · `hide` → eye-off · `delete` → delete · `calendar` → calendar · `export` → download · `share` → share-2 · `ai` → sparkles · `trash` → trash-2 |
| **Money** | `wallet` → wallet · `card` → credit-card · `income` → arrow-down-left · `expense` → arrow-up-right · `savings` → piggy-bank · `coins` → coins · `trendUp` → trending-up · `trendDown` → trending-down |
| **Categories** | `groceries` → shopping-cart · `food` → utensils · `transport` → car · `bills` → receipt · `health` → heart-pulse · `shopping` → shopping-bag · `salary` → briefcase · `travel` → plane · `laptop` → laptop |
| **Goals** | piggy-bank · plane · laptop · car · house · graduation-cap · heart · gift · shield-check |
| **Security** | `lock` → lock · `pinCreate` → lock-keyhole · `faceId` → scan-face · `changePin` → key-round · `autoLock` → timer |
| **States** | `empty` → check-check · `noResults` → search-x · `offline` → wifi-off · `serverError` → server-crash · `syncError` → cloud-off · `alert` → circle-alert · `warning` → triangle-alert · `loading` → loader-circle |
| **Settings** | `security` → shield-check · `language` → globe · `darkMode` → moon · `help` → circle-help · `logout` → log-out · `settings` → settings |

---

## 5. Spacing, radius, soyalar

### Spacing (4px asos)

| Token | px | Qayerda |
|---|---|---|
| `xs` | 4 | Ikonka va matn orasida, segmented ichki padding |
| `sm` | 8 | Chip'lar orasida, grid gap |
| `md` | 12 | List ichida ikonka–matn |
| `lg` | 16 | Karta padding, bo'limlar orasida |
| `xl` | 20 | Ekran chetidan (horizontal padding) |
| `2xl` | 24 | Katta bo'limlar, auth ekran padding |
| `3xl` | 32 | Hero bloklar |

**Ekran:** gorizontal padding 20px, bo'limlar orasida 16–22px.

### Radius

| Token | px | Qayerda |
|---|---|---|
| `sm` | 10 | Segmented ichidagi tugma |
| `md` | 12–14 | Input, kichik ikonka konteyner, chip-karta |
| `lg` | 16 | Tugma, quick action |
| `xl` | 20 | Karta, list konteyner |
| `2xl` | 24 | Balans kartasi, hero |
| `sheet` | 28 | Bottom sheet tepa burchaklari, Home header ostidagi panel |
| `full` | 999 | Pill, chip, toggle, avatar |

### Soyalar

Asosan soyasiz, 1px `border` ishlatiladi. Istisnolar:
- Toggle knob: `0 1px 3px rgba(0,0,0,0.2)`
- Segmented faol element: `0 1px 3px rgba(0,0,0,0.08)`
- Toast: `0 8px 24px rgba(6,20,14,0.18)`

---

## 6. Komponentlar

### 6.1 Tugmalar

| Variant | Fon | Matn | Balandlik | Radius |
|---|---|---|---|---|
| Primary | `primary500` | `onPrimary` | 52–56 | 16 |
| Secondary | `primary50` | `primary700` | 52 | 16 |
| Outline | `surface` + 1px `border` | `textPrimary` | 52 | 16 |
| Destructive | `dangerSoft` | `danger` | 52 | 16 |
| Destructive solid | `danger` | `#FFFFFF` | 52 | 16 |
| Dark | `textPrimary` | `surface` | 52 | 16 |
| Disabled | `divider` | `textTertiary` | — | — |
| Pill (kichik) | `primary500` yoki `primary50` | — | 36 | full |
| Icon button | `surface` + border | — | 44×44 | full |

- Matn: 15–16px, SemiBold 600. Ikonka bilan bo'lsa gap 6–8px.
- Pressed: `scale(0.96)`.
- Minimal bosish maydoni: 44×44.

### 6.2 Input

- Balandlik 50px (summa uchun 68–72px), radius 14–18, 1px `border`, padding 14–18px.
- Label: 13px SemiBold `textSecondary`, input ustida, gap 6px.
- Summa input: 30–40px Bold, o'ngda `UZS` 16–17px `textTertiary`.
- Fokus / to'ldirilgan: chegara `primary500`, 1.5px.
- Xato: chegara `danger` 1.5px + ostida 13px `danger` matn. Tasdiqlashda xato bo'lsa `shake` animatsiyasi.
- Qidiruv: `surface` fon, chapda `search` ikonkasi 18px.

### 6.3 Chip

| Holat | Fon | Matn | Chegara |
|---|---|---|---|
| Default | `surface` | `textPrimary` | 1px `border` |
| Tanlangan (filtr) | `textPrimary` | `#FFFFFF` | — |
| Tanlangan (kategoriya/sana) | `primary500` | `onPrimary` | — |
| Tinted | `primary50` | `primary700` | — |

Balandlik 36–38px, padding 0 14–16px, radius full, 14px Medium.

### 6.4 Segmented control

- Track: `background` (yoki `border`), radius 14, padding 4, gap 4.
- Element: balandlik 36–44, radius 10–12, 13–15px SemiBold.
- Faol: `surface` fon + yengil soya. Brend variant (Home tabs): `primary500` fon + `onPrimary` matn.
- Ishlatilishi: Week / Month / Year, Repeat, Auto-lock 1 / 3 / 5 min, Accounts / Cards / Loans.

### 6.5 Toggle

- 44×24, padding 2, knob 20×20 oq.
- Off: `border`, On: `primary500`. Knob `translateX(20px)`, 250ms.

### 6.6 Progress bar

- Balandlik 6–10px, radius full, track `divider`.
- Rang: < 75% `primary500` · 75–100% `warning` · > 100% `danger`.
- Qorong'u kartada track `#0B5E48`.

### 6.7 Kartalar

| Karta | Fon | Radius | Padding |
|---|---|---|---|
| Oddiy | `surface` + 1px `border` | 20 | 16 |
| Tinted (AI) | `primary50` + 1px `primary100` | 20 | 16 |
| Balans / Hero | `primary900` | 24 | 20 |
| Bo'sh holat | `surface` + 1px **dashed** `border` | 20 | 22×16 |
| Goal grid | 2 ustun, gap 10; birinchi goal to'liq kenglikda, qorong'u | 20 | 16 |

Qorong'u karta ichidagi bloklar: `#0B5E48` yoki `rgba(255,255,255,0.07)`, radius 14–16.

### 6.8 Transaction row (68px)

```
[44×44 ikonka, radius 14, cat 12%]  Title (15 Medium)          −186 400
                                    Category · 14:20 (13 tert)  (15 SemiBold)
```
- Qatorlar orasida 1px `divider`. Konteyner: oddiy karta, padding 4×16.
- Daromad: `+` va `primary700`. Xarajat: `−` (U+2212) va `textPrimary`.

### 6.9 Settings row (56px)

36×36 ikonka konteyner (`primary50`, radius 12) · label 15 Medium · qiymat 14 `textTertiary` · `chevron-right` 18.

### 6.10 Bottom sheet

- Fon `surface`, tepa radius 28, padding 10×20×34.
- Handle: 40×5, radius full, `border`, markazda.
- Sarlavha qatori: 20px SemiBold + o'ngda 40×40 yopish tugmasi (`background` fon, `x` 18).
- Scrim: `rgba(6,20,14,0.45)`, bosilsa yopiladi.
- Maksimal balandlik ~790px, ichida scroll.

### 6.11 Toast

- Pastda markazda, qorong'u fon (`textPrimary`), oq matn 14px Medium, radius full.
- Kirish animatsiyasi `fnToast`, 2.2 soniyadan keyin yo'qoladi.

### 6.12 Tab bar

- 5 ustun: Home · Activity · **[FAB]** · Stats · Budgets.
- Fon `surface`, tepada 1px `border`, pastki padding 28 (home indicator).
- Faol: ikonka va label `primary700` + ustida 18px indikator. Nofaol: `textTertiary`.
- FAB: 56–64px, `primary500`, `plus` ikonkasi `onPrimary`.

### 6.13 Quick actions

4 ustunli grid, gap 8. 56×56 konteyner (`surface` + border, radius 18), ikonka 22 `primary700`, ostida 13px Medium label.

### 6.14 PIN klaviatura

- Fon `primary900`, matn oq.
- 4 nuqta: 16×16, 2px chegara `rgba(167,243,208,0.5)`. To'lganda `primary500` + `scale(1.15)`. Xatoda `danger` va `shake`.
- Klaviatura: 3×4 grid, tugma 68px doira, raqam 28px Medium. Pressed: `rgba(255,255,255,0.16)`.
- Chap pastda Face ID (`scan-face`, `primary200`), o'ng pastda `delete`.

### 6.15 Avatar

Doira, `primary100` fon, `primary700` matn (bosh harflar, Bold). O'lchamlar: 34, 44, 72, 88. Qorong'u fonda: `rgba(167,243,208,0.16)` + `primary200`.

### 6.16 Banner

- Offline: `warningSoft` fon, `warningText` matn, `wifi-off` 16, o'ngda "Retry". Radius 14.
- Unread nuqta: 8×8 `primary500` / `primary400`, 2px fon rangidagi chegara, `pulse` animatsiya.

---

## 7. Ekran shablonlari

| Shablon | Fon | Tuzilish |
|---|---|---|
| **Home** | Header `primary950` (to'r naqsh) → panel `background`, tepa radius 28, −24px overlap | Avatar + salom + bell · balans + eye · Income/Expenses · Quick actions · Get started (yangi user) · AI · Budget · Upcoming · Recent |
| **Tab ekran** | `background` | Sarlavha 24 Bold · kontent kartalar · tab bar |
| **Push ekran** | `background` | 44px back tugma + sarlavha 17–20 SemiBold · kontent |
| **Auth / Setup** | `surface` | padding 24 · sarlavha 28/34 Bold · matn 15/22 · pastda Primary + text tugma |
| **Dark full-screen** | `primary900` | Splash, Onboarding, PIN create, PIN lock |
| **Scanner** | `#0B0F0D` | Kamera ko'rinishi + animatsiyali chiziq |

**Status bar:** Home'da `primary950` + oq ikonkalar; dark ekranlarda `primary900`; Auth'da `surface`; qolganlarida `background`.

---

## 8. Holatlar: bo'sh, xato, yuklanish

### Bo'sh holat (to'liq ekran)
- 96–120px doira (`primary50`) ichida 60px kvadrat (`primary500`, radius 20) + ikonka 28 `onPrimary`, `float` animatsiya.
- Sarlavha 18 Bold · matn 14/20 `textSecondary`, max 260px · tugma(lar).

### Bo'sh holat (inline karta)
- Dashed chegara karta · 48px ikonka (`primary50`) · 16 SemiBold sarlavha · 14 matn · kichik secondary tugma "+ …".

| Joy | Sarlavha | CTA |
|---|---|---|
| Activity | No transactions yet | Add transaction · Scan receipt |
| Statistics | Not enough data yet | Add transaction |
| Budgets | No budgets set | Set a limit |
| Goals | No savings goals | New goal |
| Reminders | No payment reminders | Add reminder |
| Notifications | You're all caught up | — |
| Search | Nothing found | Clear filters |

### Xato holatlari
- Fon `dangerSoft`, ikonka `danger`, `shake` animatsiya.
- Turlar: offline (`wifi-off`), server (`server-crash`), sync (`cloud-off`), QR topilmadi, noto'g'ri OTP / PIN.

### Birinchi kirish (yangi user)
- Balans 0, header'da "Add your current balance" pill.
- "Get started" checklist (4 qadam, progress doira): balans · birinchi tranzaksiya · goal · reminder.

---

## 9. Animatsiya

**Asosiy easing:** `cubic-bezier(.2,.8,.2,1)` · sheet uchun `cubic-bezier(.2,.9,.3,1)`.

| Nomi | Davomiylik | Nima qiladi | Qayerda |
|---|---|---|---|
| `fnIn` | 450ms | opacity 0→1, Y +14→0 | Ekran, list elementlari |
| `fnPush` | 420ms | opacity 0→1, X +32→0 | Push ekran, gorizontal kartalar |
| `fnFade` | 300–500ms | opacity | Scrim, dark ekranlar |
| `fnSheet` | 420ms | Y 100%→0 | Bottom sheet |
| `fnPop` | 500–600ms | scale .6→1.06→1 | Bo'sh holat ikonka, belgi |
| `fnToast` | — | Y +18, scale .94→1 | Toast |
| `fnBar` | 1000–1100ms | scaleX 0→1 | Progress bar |
| `fnShake` | 450ms | X ±8 | Xato input, PIN |
| `fnRing` | 3.2s ∞ | bell tebranishi | O'qilmagan bildirishnoma |
| `fnPulse` | 2s ∞ | unread nuqta | Bell |
| `fnFloat` | 3.5–4s ∞ | Y ±… | Bo'sh holat ikonka |
| `fnGlow` | 2.4s ∞ | yorqinlik | AI ikonka |

- **Stagger:** list elementlari 40–90ms qadam bilan.
- **Press:** `scale(0.96)` (kartalar 0.97–0.98).
- **Home scroll:** balans kartasi parallax (`translateY(y*0.35)`, `scale(1 - y/1400)`), 240px'da yo'qoladi; tepada sticky mini-bar paydo bo'ladi.
- `prefers-reduced-motion` yoqilgan bo'lsa, cheksiz animatsiyalar o'chiriladi.

---

## 10. Dark mode

| Token | Light | Dark |
|---|---|---|
| `background` | `#F4F7F5` | `#0B1210` |
| `surface` | `#FFFFFF` | `#141D19` |
| `textPrimary` | `#0E1A14` | `#E8EFEB` |
| `textSecondary` | `#56655D` | `#A3B1A9` |
| `textTertiary` | `#8B988F` | `#76857D` |
| `textDisabled` | `#C3CDC7` | `#3A4741` |
| `border` | `#E4EAE6` | `#24302B` |
| `divider` | `#EEF2EF` | `#1C2622` |
| `tint` (primary50) | `#ECFDF5` | `#0F2A21` |
| `tint2` (primary100) | `#D1FAE5` | `#15503C` |
| `primaryText` (primary700) | `#047857` | `#34D399` |
| `danger` | `#DC2626` | `#F87171` |

- `primary500`, kategoriya ranglari va qorong'u yashil kartalar ikkala rejimda bir xil.
- Profile → Dark mode toggle. Tanlov qurilmada saqlanishi kerak (prototipda hali saqlanmaydi).

---

## 11. Raqamlar va matn formatlash

- **Minglik ajratgich:** bo'sh joy — `24 850 000`.
- **Valyuta:** summadan keyin — `24 850 000 UZS`. Tiyin ko'rsatilmaydi.
- **Belgi:** daromad `+12 500 000`, xarajat `−186 400` (minus U+2212, defis emas).
- **Qisqa format:** `1.2M`, `850K` (grafik, goal kartalari).
- **Yashirilgan balans:** `•••••••`.
- **Sana:** `Today`, `Yesterday`, `28 Sep`, `Dec 2027`. Vaqt 24 soatlik — `14:20`.
- **Telefon:** `+998 90 123 45 67`, maskalangan: `+998 90 *** ** 67`.
- **Karta:** `•••• 4821`.
- **Matn uslubi:** qisqa, to'g'ridan-to'g'ri. Sarlavhalarda faqat birinchi so'z bosh harf bilan (`Recent transactions`). Undov belgisi va emoji yo'q.

---

## 12. Accessibility

- Matn kontrasti ≥ 4.5:1 (katta sarlavhalar ≥ 3:1).
- `primary500` ustida faqat `onPrimary` (`#052E1F`).
- Bosish maydoni ≥ 44×44.
- Rang yagona signal emas: limitdan oshganda qizil + "Over by … UZS" matni.
- Ikonka-tugmalarda `Semantics(label: …)`.
- Dinamik shrift o'lchami: 1.3x gacha layout buzilmasligi kerak.

---

## 13. Flutter kodi

### AppColors

```dart
import 'package:flutter/material.dart';

abstract class AppColors {
  // Primary
  static const primary50  = Color(0xFFECFDF5);
  static const primary100 = Color(0xFFD1FAE5);
  static const primary200 = Color(0xFFA7F3D0);
  static const primary300 = Color(0xFF6EE7B7);
  static const primary400 = Color(0xFF34D399);
  static const primary500 = Color(0xFF10B981);
  static const primary600 = Color(0xFF059669);
  static const primary700 = Color(0xFF047857);
  static const primary800 = Color(0xFF065F46);
  static const primary900 = Color(0xFF064E3B);
  static const primary950 = Color(0xFF052E1F);

  // Neutral
  static const textPrimary   = Color(0xFF0E1A14);
  static const textSecondary = Color(0xFF56655D);
  static const textTertiary  = Color(0xFF8B988F);
  static const textDisabled  = Color(0xFFC3CDC7);
  static const border        = Color(0xFFE4EAE6);
  static const divider       = Color(0xFFEEF2EF);
  static const background    = Color(0xFFF4F7F5);
  static const surface       = Color(0xFFFFFFFF);
  static const scrim         = Color(0x7306140E);

  // Semantic
  static const success     = primary500;
  static const danger      = Color(0xFFDC2626);
  static const dangerSoft  = Color(0xFFFEF2F2);
  static const warning     = Color(0xFFF59E0B);
  static const warningText = Color(0xFFB45309);
  static const warningSoft = Color(0xFFFEF3C7);
  static const info        = Color(0xFF3B82F6);
  static const onPrimary   = primary950;

  // Categories
  static const catGroceries = Color(0xFF10B981);
  static const catFood      = Color(0xFFF59E0B);
  static const catTransport = Color(0xFF3B82F6);
  static const catBills     = Color(0xFF8B5CF6);
  static const catHealth    = Color(0xFFEF4444);
  static const catShopping  = Color(0xFFEC4899);
  static const catHousing   = Color(0xFF14B8A6);
  static const catSubs      = Color(0xFF6366F1);
  static const catTransfer  = Color(0xFF0EA5E9);

  static Color tintOf(Color c) => c.withOpacity(0.12);
}

abstract class AppColorsDark {
  static const background    = Color(0xFF0B1210);
  static const surface       = Color(0xFF141D19);
  static const textPrimary   = Color(0xFFE8EFEB);
  static const textSecondary = Color(0xFFA3B1A9);
  static const textTertiary  = Color(0xFF76857D);
  static const textDisabled  = Color(0xFF3A4741);
  static const border        = Color(0xFF24302B);
  static const divider       = Color(0xFF1C2622);
  static const tint          = Color(0xFF0F2A21);
  static const tint2         = Color(0xFF15503C);
  static const primaryText   = Color(0xFF34D399);
  static const danger        = Color(0xFFF87171);
}
```

### AppTextStyles

```dart
import 'dart:ui';
import 'package:flutter/material.dart';

abstract class AppTextStyles {
  static const _f = 'Onest';
  static const _tab = [FontFeature.tabularFigures()];

  static const displayLarge = TextStyle(fontFamily: _f, fontSize: 40, height: 48 / 40, fontWeight: FontWeight.w700, letterSpacing: -1.2, fontFeatures: _tab);
  static const display      = TextStyle(fontFamily: _f, fontSize: 32, height: 40 / 32, fontWeight: FontWeight.w700, letterSpacing: -0.64, fontFeatures: _tab);
  static const headline     = TextStyle(fontFamily: _f, fontSize: 24, height: 32 / 24, fontWeight: FontWeight.w700, letterSpacing: -0.24);
  static const title        = TextStyle(fontFamily: _f, fontSize: 20, height: 28 / 20, fontWeight: FontWeight.w600);
  static const titleSmall   = TextStyle(fontFamily: _f, fontSize: 17, height: 24 / 17, fontWeight: FontWeight.w600);
  static const body         = TextStyle(fontFamily: _f, fontSize: 15, height: 22 / 15, fontWeight: FontWeight.w400);
  static const bodyMedium   = TextStyle(fontFamily: _f, fontSize: 15, height: 22 / 15, fontWeight: FontWeight.w500);
  static const caption      = TextStyle(fontFamily: _f, fontSize: 13, height: 18 / 13, fontWeight: FontWeight.w400);
  static const label        = TextStyle(fontFamily: _f, fontSize: 12, height: 16 / 12, fontWeight: FontWeight.w600, letterSpacing: 0.72); // UPPERCASE
  static const tabLabel     = TextStyle(fontFamily: _f, fontSize: 11, height: 14 / 11, fontWeight: FontWeight.w500);
  static const amount       = TextStyle(fontFamily: _f, fontSize: 15, height: 22 / 15, fontWeight: FontWeight.w600, fontFeatures: _tab);
}
```

### AppSpacing / AppRadius / AppMotion

```dart
abstract class AppSpacing {
  static const xs = 4.0, sm = 8.0, md = 12.0, lg = 16.0, xl = 20.0, x2l = 24.0, x3l = 32.0;
  static const screen = 20.0;
}

abstract class AppRadius {
  static const sm = 10.0, md = 14.0, lg = 16.0, xl = 20.0, x2l = 24.0, sheet = 28.0, full = 999.0;
}

abstract class AppMotion {
  static const ease      = Cubic(0.2, 0.8, 0.2, 1);
  static const easeSheet = Cubic(0.2, 0.9, 0.3, 1);
  static const fast   = Duration(milliseconds: 250);
  static const normal = Duration(milliseconds: 420);
  static const slow   = Duration(milliseconds: 1100);
  static const stagger = Duration(milliseconds: 50);
  static const pressScale = 0.96;
}
```

### Formatlash

```dart
String formatUzs(num v, {bool sign = false}) {
  final s = v.abs().round().toString()
      .replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (_) => ' ');
  if (!sign) return s;
  return (v >= 0 ? '+' : '\u2212') + s;
}

String formatShort(num v) => v >= 1e6
    ? '${(v / 1e6).toStringAsFixed(2).replaceAll(RegExp(r'\.?0+$'), '')}M'
    : '${(v / 1000).round()}K';
```
