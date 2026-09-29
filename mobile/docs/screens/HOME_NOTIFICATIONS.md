# Finora — Home, yangi foydalanuvchi holati, Notifications

Versiya 1.0 · 28.09.2026 · Flutter (iOS / Android)

Home va Notifications ekranlarining to'liq spetsifikatsiyasi: ma'lumotli holat, yangi foydalanuvchi (bo'sh) holati, empty/offline holatlar.

Bog'liq hujjatlar:
- `docs/DESIGN_SYSTEM.md` — tokenlar
- `docs/screens/AUTH_SCREENS.md` — umumiy qoidalar
- `docs/screens/PIN_SETUP_SCREENS.md` — Create PIN, PIN lock, Starting balance

---

## 0. AI uchun ko'rsatma (prompt)

> Quyidagi spetsifikatsiya va skrinshotlar asosida Flutter kodini yoz.
> - Faqat `DESIGN_SYSTEM.md` tokenlaridan foydalan.
> - Fayllar: `home_screen.dart`, `notifications_screen.dart`. Bo'limlar alohida vidjet: `home_hero.dart`, `quick_actions.dart`, `get_started_card.dart`, `ai_insight_card.dart`, `budget_summary_card.dart`, `upcoming_payments.dart`, `recent_transactions.dart`, `empty_card.dart`, `balance_sheet.dart`, `notification_tile.dart`.
> - Home `CustomScrollView` + `SliverAppBar` (collapse animatsiyasi uchun).
> - Riverpod, `go_router`, `lucide_icons`, Onest.
> - Summalar: `NumberFormat('#,###', 'uz')` → bo'sh joy bilan (`12 500 000`), tabular raqamlar (`FontFeature.tabularFigures()`).
> - Matnlarni o'zgartirma. Press effekti `scale 0.96`, 120ms.

---

## 1. Yangi foydalanuvchi qaysi oynani ko'radi

Starting balance'dan keyin foydalanuvchi **Home**ga tushadi. Ma'lumot yo'q, shuning uchun Home "yangi foydalanuvchi" rejimida:

| Blok | Ma'lumotli (oddiy) | Yangi foydalanuvchi |
|---|---|---|
| Balans | haqiqiy balans | kiritilgan summa yoki `0` |
| "Add your current balance" tugmasi | yo'q | balans kiritilmagan bo'lsa (Skip) |
| Income / Expenses | oy summasi | `0` / `0` |
| Quick actions | bor | bor |
| **Get started** checklist | yo'q | bor (4 banddan kamida bittasi bajarilmagan) |
| Finora AI kartasi | bor | **yashirin** |
| September budget kartasi | bor | **yashirin** |
| Upcoming payments | gorizontal kartalar | empty karta "No payments scheduled" |
| Recent transactions | ro'yxat (4 ta) | empty karta "No transactions yet" |
| Qo'ng'iroq | badge + tebranish | badge yo'q, tebranish yo'q |
| Notifications ekrani | ro'yxat | "You're all caught up" |

Mantiq:

```dart
final isFresh = user.isNew;          // onboarding'dan keyin true
final needBalance = isFresh && !user.balanceSet;
final showChecklist = isFresh && checklistDone < 4;
final showInsights = !isFresh;       // AI + budget kartalari
```

`isFresh` 4 ta band bajarilgach `false` bo'ladi (yoki server tomonda: kamida 7 kunlik ma'lumot). Shundan keyin checklist yo'qoladi, AI va budget kartalari paydo bo'ladi.

Yangi foydalanuvchi uchun boshqa tablar ham bo'sh holatda: Activity — "No transactions yet", Stats — "Not enough data yet", Budgets — "No budgets set" + "No savings goals".

---

## 2. Umumiy

| Parametr | Qiymat |
|---|---|
| Home foni | yuqori qism `primary950` `#052E1F`, kontent `background` `#F4F7F5` |
| Status bar (Home) | oq ikonkalar |
| Status bar (Notifications) | qora ikonkalar (dark mode'da oq) |
| Kontent padding | gorizontal 20 |
| Karta | fon `surface`, chegara 1px `border`, radius 20 |
| Empty karta | fon `surface`, chegara 1px **dashed** `border`, radius 20 |
| Bottom nav | faqat Home, Activity, Stats, Budgets'da |

### Bottom navigation

```
Container (bg surface, border-top 1px border, padding 8 12 28 12)
└─ Grid 5 ustun: 1fr 1fr 72 1fr 1fr
   Home · Activity · [FAB +] · Stats · Budgets
```

| Tab | Ikonka | Route |
|---|---|---|
| Home | `house` | `/home` |
| Activity | `arrow-left-right` | `/activity` |
| Stats | `chart-pie` | `/stats` |
| Budgets | `target` | `/budgets` |

- Tab: h 52, ikonka 22, label 11 Medium, gap 4. Faol: `primary700`; nofaol: `textTertiary`.
- Faol indikator: label ostida 3px chiziq, `primary500`, kenglik 0 → 18 (300ms).
- FAB: 56×56 doira, `primary500`, Lucide `plus` 26 `onPrimary`, marginTop −22, soya `0 8 20 rgba(16,185,129,0.35)`. Bosilganda "New transaction" bottom sheet.

---

## 3. Home

**Route:** `/home` · **Fayl:** `home_screen.dart`

### Tuzilish

```
Scaffold (bg: primary950)
├─ CustomScrollView
│  ├─ HomeHero (qorong'u, paddingBottom 48)
│  │  ├─ Header: Avatar · Salom · Bell
│  │  ├─ Balance row + (shartli) "Add your current balance"
│  │  └─ Income / Expenses
│  └─ Content (bg background, radius 28 28 0 0, marginTop −24, padding 22 20 28, gap 22)
│     ├─ OfflineBanner (shartli)
│     ├─ QuickActions (4)
│     ├─ GetStartedCard (yangi foydalanuvchi)
│     ├─ AiInsightCard (oddiy)
│     ├─ BudgetSummaryCard (oddiy)
│     ├─ UpcomingPayments
│     └─ RecentTransactions
├─ CollapsedBar (sticky, scroll'da paydo bo'ladi)
└─ BottomNav
```

### 3.1 HomeHero

Fon: `primary950` + radial gradient `120% 80% at 100% 0%`: `#0B5E48 0%` → `#052E1F 60%`. Ustida ±45° juda nozik chiziqli naqsh (`rgba(167,243,208,0.035)`, 1px, qadam 44). Padding `8 20 48 20`, gap 26.

| Element | Spetsifikatsiya |
|---|---|
| Avatar | 44×44 doira, fon `rgba(167,243,208,0.16)`, "DK" 15 Bold `primary200`. Bosilganda → `/profile` |
| Salom | "Good morning" 13 `primary200` / ism "Doston" 17 SemiBold oq. Vaqtga qarab: Good morning (5–12), Good afternoon (12–18), Good evening (18–5) |
| Bell | 44×44, Lucide `bell` 22 oq. → `/notifications` |
| Unread badge | 8×8 doira, `#34D399`, chegara 2px `#052E1F`, top 9 right 10. Pulse animatsiya |
| Balans | 34 Bold, letterSpacing −0.68, tabular, oq + " UZS" 18 SemiBold `primary200` |
| Eye tugma | 44×44, `eye` / `eye-off` 22. Yashirilganda balans `•••••••` |
| "Add your current balance" | faqat `needBalance`. h 36, padding `0 14 0 10`, radius full, `primary500`, `plus` 16 + matn 14 SemiBold `onPrimary`, gap 6. → Balance sheet (3.4) |
| Income / Expenses | 2 ta teng karta, gap 8. Fon `rgba(255,255,255,0.07)`, radius 16, padding 10, gap 8 |
| — ikonka | 28×28, radius 9. Income: `primary500` fon, `arrow-down-left` `onPrimary`. Expenses: `primary200` fon, `arrow-up-right` `primary900` |
| — matn | label 12 `primary200` / summa 13 SemiBold oq, bir qatorda |

### 3.2 Scroll animatsiyasi

`y` = scroll offset.

| Qiymat | Formula |
|---|---|
| Hero translateY | `y × 0.35` |
| Hero scale | `1 − y / 1400` |
| Hero opacity | `max(0, 1 − y / 240)` |
| Header opacity | `max(0, 1 − y / 90)` |
| CollapsedBar opacity | `p` = `clamp((y − 120) / 60, 0, 1)` |
| CollapsedBar translateY | `(1 − p) × −10` |

**CollapsedBar:** h 60, padding 0 20, fon `primary950`, gap 12. Avatar 34×34 ("DK" 12 Bold) · "TOTAL BALANCE" 11 SemiBold uppercase letterSpacing 0.66 `primary200` + summa 17 Bold · "Add" tugmasi (h 36, radius full, `primary500`, `plus` 16 + 14 SemiBold). `p < 0.5` bo'lsa bosilmaydi.

### 3.3 Content bloklari

**OfflineBanner** (internet yo'q bo'lsa): padding 10 14, radius 14, fon `warningSoft` `#FEF3C7`, matn `warning` `#B45309` 13 Medium. `wifi-off` 16 + "You're offline. Showing data from {HH:mm}." + "Retry" 13 Bold. Retry → toast "Reconnecting…".

**QuickActions:** 4 ustunli grid, gap 8. Har biri: 56×56 radius 18 `surface` + 1px `border`, ikonka 22 `primary700`; label 13 Medium `textSecondary`, gap 8.

| Label | Ikonka | Amal |
|---|---|---|
| Add | `plus` | New transaction sheet |
| Scan | `scan-line` | `/scan` |
| Reminders | `bell-ring` | `/reminders` |
| Goals | `target` | `/budgets` |

**GetStartedCard** (yangi foydalanuvchi): karta, padding `16 16 6 16`, gap 4.

- Sarlavha qatori: "Get started" 17 SemiBold / "{n} of 4 done" 13 `textSecondary`. O'ngda progress halqa 44×44: `SweepGradient` `primary500` (n/4 × 360°) + `divider`; ichida 34×34 `surface` doira, "{pct}%" 12 Bold `primary700`.
- Bandlar (har biri: padding 10 0, border-top 1px `divider`, gap 12):

| # | Label | Sub | Bajarilgan sharti | Bosilganda |
|---|---|---|---|---|
| 1 | Set your current balance | So your total is accurate | balans kiritilgan | Balance sheet |
| 2 | Add your first transaction | An expense or income | ≥1 tranzaksiya | New transaction sheet |
| 3 | Create a savings goal | Trip, car, emergency fund | ≥1 maqsad | `/budgets` + New goal sheet |
| 4 | Add a payment reminder | Rent, internet, subscriptions | ≥1 eslatma | `/reminders` + New reminder sheet |

| Band holati | Doira 26×26 | Label | O'ng |
|---|---|---|---|
| Bajarilmagan | chegara 2px `border` | 15 Medium `textPrimary` | `chevron-right` 18 `textTertiary` |
| Bajarilgan | `primary500` + `check` 14 `onPrimary` | `textTertiary`, chizilgan | yo'q, bosilmaydi |

4/4 bo'lganda karta fade-out bilan yo'qoladi.

**AiInsightCard** (oddiy): fon `primary50`, chegara 1px `primary100` `#D1FAE5`, radius 20, padding 16, gap 14. Ikonka 44×44 radius 14 `primary500` + `sparkles` 22 (glow animatsiya). "FINORA AI" 12 SemiBold uppercase `primary700` / "You could save {amount} UZS this month" 15/20 SemiBold. `chevron-right`. → `/insights`.

**BudgetSummaryCard** (oddiy): karta, padding 16, gap 12. "{Month} budget" 15 SemiBold · "{n} days left" 13 `textSecondary`. "{spent}" 17 SemiBold + " of {limit} UZS" 13. Progress h 8, track `divider`, to'ldirish `primary500`. → `/budgets`.

**UpcomingPayments:** sarlavha "Upcoming payments" 17 SemiBold + "See all" 14 SemiBold `primary700` (→ `/reminders`).
- Ma'lumotli: gorizontal scroll, gap 10, kartalar 164 kenglik, padding 14, gap 10. Ikonka 36×36 radius 12 (kategoriya rangi 12% fon). Nomi 15 SemiBold (ellipsis), summa 14 tabular, muddat 12 SemiBold.
- Muddat rangi: bugun "Due today" `danger`; ertaga "Due tomorrow" `warning`; ≤14 kun "In {n} days" `textSecondary`; boshqa "{d} {Mon}" `textTertiary`.

**RecentTransactions:** sarlavha "Recent transactions" + "See all" (→ `/activity`).
- Ma'lumotli: bitta karta, padding 4 16, oxirgi 4 ta. Qator: padding 12 0, gap 12, ikonka 44×44 radius 14, nomi 15 Medium, sub 13 `textTertiary` ("Category · 14:20"), summa 15 SemiBold (income `primary700` "+", expense `textPrimary` "−").

### 3.4 Empty holatlar (Home ichida)

| Blok | Ikonka (48×48 yoki 40×40, `primary50` fon) | Sarlavha | Matn | Tugma / amal |
|---|---|---|---|---|
| Upcoming payments | `bell-plus` 20 (40×40, radius 12) | No payments scheduled | Add rent, internet or subscriptions | butun karta bosiladi → `/reminders` + New reminder; o'ngda `plus` 18 |
| Recent transactions | `receipt` 22 (48×48, radius 15) | No transactions yet | Add your first expense or income, or scan a receipt. | "Add transaction" (h 40, radius 12, `primary50` fon, `primary700`, `plus` 16) → New transaction |

- Payments empty: gorizontal qator, padding 14 16, gap 12, sarlavha 15 SemiBold, matn 13 `textSecondary`.
- Transactions empty: markazlashgan ustun, padding 22 16, gap 10; sarlavha 16 SemiBold, matn 14/20 `textSecondary` maxWidth 260.

### 3.5 Balance sheet

Home'dagi "Add your current balance" yoki checklist 1-band ochadi.

```
ModalBottomSheet (radius 28 28 0 0, padding 10 20 34, gap 16)
├─ Handle 40×5 `border`
├─ Header: "Current balance" 20 SemiBold / "Cash and cards combined" 13 · Close (40×40, `x` 18)
├─ AmountField (h 68, 30 Bold, "UZS")
├─ QuickChips +100K · +1M · +5M
└─ "Save balance" (h 56)
```

- Holatlar Starting balance bilan bir xil (summa 0 → disabled).
- Save → balans = kiritilgan summa + oy daromadi − xarajat; toast **"Balance updated"**; checklist 1-band bajariladi, hero tugmasi yo'qoladi.
- Barrier: `rgba(6,20,14,0.45)`, fade 300ms. Sheet: slide up 420ms `Cubic(0.2,0.9,0.3,1)`.

### 3.6 Animatsiyalar

| Element | Animatsiya | Davomiylik / kechikish |
|---|---|---|
| Ekran | fade + Y +14 → 0 | 450ms |
| QuickActions | shu animatsiya, stagger | 0 / 40 / 80 / 120ms |
| GetStartedCard | fade + Y | 500ms, 100ms |
| AiInsightCard | fade + Y; ikonka glow (box-shadow 0 → 7px), cheksiz | 500ms, 150ms; glow 2400ms |
| Budget progress | scaleX 0 → 1 | 1100ms, 200ms |
| Payment kartalari | push X +32 → 0, stagger 60ms | 500ms |
| Tranzaksiya qatorlari | fade + Y, stagger 60ms | 450ms |
| Bell (unread bor) | tebranish 0 → 14° → −12° → 8° → −4° → 0 (sikl 70–90% oralig'ida) | 3200ms, cheksiz |
| Unread badge | pulse halqa 0 → 8px | 2000ms, cheksiz |
| FAB | pop | 600ms, 150ms |

`MediaQuery.disableAnimations` → cheksiz animatsiyalar o'chadi.

---

## 4. Notifications

**Route:** `/notifications` · **Fayl:** `notifications_screen.dart`

### Tuzilish

```
Scaffold (bg: background)
└─ SafeArea → ListView (padding 8 20 28, gap 16)
   ├─ TopBar (gap 12)
   │  ├─ Back 44×44
   │  ├─ "Notifications" (flex)
   │  ├─ "Mark all read"
   │  └─ Clear (trash)
   ├─ Group "Today"
   ├─ Group "Earlier"
   └─ EmptyState (shartli)
```

### Elementlar

| Element | Spetsifikatsiya |
|---|---|
| Back | 44×44 doira, `surface` + 1px `border`, `chevron-left` 20 `textPrimary` → `/home` |
| Title | 17 SemiBold |
| "Mark all read" | h 36, 14 SemiBold. Unread bor: `primary700`; yo'q: `textTertiary` |
| Clear | 40×40 doira, `trash-2` 18 `textSecondary` |
| Guruh sarlavhasi | 13 SemiBold `textSecondary`, padding 0 4, gap 8 |
| Guruh kartasi | `surface`, 1px `border`, radius 20, padding 0 16 |
| Tile | padding 14 0, gap 12, `crossAxisAlignment.start`, ikkinchisidan boshlab border-top 1px `divider` |
| — ikonka | 40×40 radius 12, fon = rang 12% (`color.withOpacity(0.12)`), ikonka 20 |
| — title | 15 SemiBold; o'ngda vaqt 12 `textTertiary` |
| — body | 14/20 `textSecondary`, gap 3 |
| — unread nuqta | 8×8 `primary500`, marginTop 6, pulse |

### Bildirishnoma turlari

| Tur | Ikonka | Rang | Bosilganda | Misol |
|---|---|---|---|---|
| `payment_due` | `bell-ring` | `#F59E0B` | `/reminders` | Payment due tomorrow · Electricity · 142 000 UZS is due on 29 Sep. |
| `income` | `arrow-down-left` | `#10B981` | `/activity` | Salary received · +12 500 000 UZS from Acme LLC arrived on Uzcard •• 4821. |
| `budget_exceeded` | `triangle-alert` | `danger` | `/budgets` | Food budget exceeded · You've spent 920 000 of 800 000 UZS on Food & drinks. |
| `weekly_report` | `chart-pie` | `#3B82F6` | `/stats` | Weekly report is ready · You spent 8% less than last week. Tap to see details. |
| `goal_milestone` | `piggy-bank` | `#10B981` | `/budgets` | Goal milestone · Samarkand trip is 62% funded. Keep going. |
| `security` | `shield-check` | `textSecondary` | `/profile` | New sign-in · Finora was opened on a new device in Tashkent. |

### Guruhlash va vaqt

| Guruh | Qoidasi | Vaqt formati |
|---|---|---|
| Today | bugun | `HH:mm` (10:00) |
| Earlier | bugundan oldin | ≤6 kun: hafta kuni (Mon); undan eski: `d MMM` (20 Sep) |

### Xatti-harakat

- Tile bosilsa → o'qilgan deb belgilanadi va tegishli ekranga o'tadi.
- **Mark all read** → barcha unread nuqtalar yo'qoladi, Home'dagi badge va bell tebranishi to'xtaydi.
- **Clear** → ro'yxat tozalanadi → EmptyState. (Production: tasdiqlash yoki 4 soniyalik "Undo" snackbar tavsiya etiladi.)
- Tile'ni chapga surish (swipe) → o'chirish (ixtiyoriy, `Dismissible`).
- Pull-to-refresh → serverdan yangilash.

### Empty holat

Ro'yxat bo'sh bo'lganda (yangi foydalanuvchi yoki Clear'dan keyin):

```
Column (markazda, padding 56 12, gap 16)
├─ Illustration: 120×120 doira `primary50`
│  └─ 68×68 radius 22 `primary500` + `check-check` 30 `onPrimary` (float animatsiya)
├─ "You're all caught up" 20 Bold
└─ "New alerts about budgets, payments and income will appear here." 15/22 `textSecondary`, maxWidth 280
```

> Prototipdagi "Restore demo alerts" tugmasi faqat demo uchun, production'da **yo'q**. Yangi foydalanuvchida TopBar'dagi "Mark all read" `textTertiary` (nofaol), Clear yashirin.

### Animatsiyalar

| Element | Animatsiya | Davomiylik |
|---|---|---|
| Ekran | push X +32 → 0 | 420ms |
| Tile'lar | fade + Y +14 → 0, stagger 60ms | 450ms |
| Unread nuqta | pulse | 2000ms, cheksiz |
| Empty illustration | pop (tashqi), float Y 0 → −8 → 0 (ichki) | 600ms; 3500ms cheksiz |

---

## 5. Qabul mezonlari

- [ ] Starting balance'dan keyin Home yangi foydalanuvchi holatida: checklist bor, AI va budget kartalari yo'q.
- [ ] Skip qilingan bo'lsa hero'da "Add your current balance" ko'rinadi; balans saqlangach yo'qoladi.
- [ ] Checklist bandlari haqiqiy ma'lumotga qarab avtomatik bajariladi; 4/4 da karta yo'qoladi.
- [ ] Payments va Transactions bo'lsa empty kartalar o'rniga ro'yxat chiqadi.
- [ ] Balans eye tugmasi bilan yashiriladi (hero va CollapsedBar'da).
- [ ] Scroll'da hero yig'iladi, CollapsedBar paydo bo'ladi.
- [ ] Offline'da banner chiqadi, Retry ishlaydi.
- [ ] Unread bo'lsa bell tebranadi va badge bor; "Mark all read"dan keyin ikkalasi yo'qoladi.
- [ ] Notification bosilsa to'g'ri ekranga o'tadi.
- [ ] Bo'sh ro'yxatda "You're all caught up".
- [ ] Dark mode'da barcha ranglar tokenlar orqali almashadi.
