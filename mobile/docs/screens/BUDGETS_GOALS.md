# Finora — Budgets & goals, Goal details, New goal

Versiya 1.0 · 28.09.2026 · Flutter

Bog'liq: `docs/DESIGN_SYSTEM.md`, `docs/screens/ACTIVITY_SCAN.md` (kategoriyalar, sheet qoidalari, empty pattern).

Skrinshotlar (`docs/screenshots/`):

| Fayl | Nima |
|---|---|
| `31-budgets-goals.png` / `31-budgets-goals-full.png` | Budgets & goals |
| `30-budgets-empty.png` | Yangi foydalanuvchi |
| `32-goal-details.png` / `32-goal-details-full.png` | Goal details |
| `33-goal-add-money.png` | Add money sheet |
| `34-goal-delete.png` | O'chirishni tasdiqlash |
| `35-new-goal.png` | New goal sheet |
| `71-dark-budgets.png` | Dark mode |

---

## 0. AI uchun ko'rsatma (prompt)

> Spetsifikatsiya va skrinshotlar asosida Flutter kodini yoz.
> - Fayllar: `budgets_screen.dart`, `budget_card.dart`, `goal_card.dart`, `goal_details_screen.dart`, `goal_fund_sheet.dart`, `goal_delete_sheet.dart`, `new_goal_sheet.dart`, `dashed_empty_card.dart`.
> - Modellar: `Budget {categoryId, limit}`, `Goal {id, name, icon, saved, target, due, autoSave, history}`.
> - Riverpod, `go_router` (`/budgets`, `/goals/:id`). Matnlarni o'zgartirma.

---

## 1. Budgets & goals ekrani

Bottom nav'da "Budgets" tab. Padding 8 20 28, gap 16.

```
"Budgets & goals" 24/700
[yangi foydalanuvchi] DashedEmptyCard "No budgets set"
BudgetCard × n (gap 10)
Row (margin-top 8): "Savings goals" 17/600 ··· pill h36 tint: plus 16 + "New goal" 14/600 → New goal sheet
Goals grid 2 ustun, gap 10 (birinchi goal — hero, ikki ustunni egallaydi)
[maqsad yo'q] DashedEmptyCard "No savings goals"
```

### 1.1 BudgetCard

| Element | Qiymat |
|---|---|
| Karta | surface, 1px border, r20, padding 16, gap 12 |
| Yuqori qator | ikon 40 r12 tint · nom 15/600 + `"1 840 000 of 2 500 000 UZS"` 13 ink2 tabular · foiz 15/600 |
| Progress | h8 r999 `divider`; to'ldirish `min(p,1)` |
| Pastki matn | 13/500 |

Rang qoidasi (`p = spent / limit`):

| Holat | Shart | Bar | Foiz rangi | Pastki matn |
|---|---|---|---|---|
| Normal | p < 0.75 | `#10B981` | ink | `660 000 UZS left` ink2 |
| Ogohlantirish | 0.75 ≤ p ≤ 1 | `#F59E0B` | ink | `{left} UZS left` ink2 |
| Oshgan | p > 1 | `danger` | danger | `Over by 120 000 UZS` danger |

Namuna: Groceries 1 840 000/2 500 000 (74%) · Food & drinks 920 000/800 000 (115%) · Shopping 1 150 000/1 500 000 (77%) · Transport 460 000/600 000 (77%).

Animatsiya: karta `fnIn` stagger 70ms; bar `fnBar` scaleX 0→1 (chapdan), 1s, shu delay bilan.

### 1.2 GoalCard

| | Hero (1-goal) | Oddiy |
|---|---|---|
| Fon | `#064E3B` | surface |
| Matn | oq | ink |
| Sub | `#A7F3D0` | ink2 |
| Ikon box | 40 r12 `#10B981`, ikon `#052E1F` | 40 r12 tint, ikon primary |
| Track | `#0B5E48` | divider |
| Grid | `grid-column: 1 / -1` | 1 ustun |

Tarkib (padding 16, gap 12, r20, 1px border): ikon ··· foiz 13/600 · nom 15/600 · `"12M / 30M · Dec 2027"` 13 tabular (`short()`) · progress h6 `#10B981` (`fnBar` 1.1s). Tap → Goal details. Press `scale 0.97`.

Namuna: Emergency fund (`shield-check`) 12 000 000/30 000 000 Dec 2027 · New MacBook (`laptop`) 6 200 000/18 000 000 Mar 2027 · Samarkand trip (`plane`) 3 100 000/5 000 000 Jun 2027.

### 1.3 DashedEmptyCard (`30-budgets-empty.png`)

Karta: surface, 1px **dashed** border, r20, padding 22 16, gap 10, markazda. Ikon box 48 r15 tint, ikon 22 primary. Sarlavha 16/600, matn 14/20 ink2 max 260. Tugma h40 r12 tint: plus 16 + label 14/600 primary.

| Blok | Ikon | Sarlavha | Matn | Tugma → |
|---|---|---|---|---|
| Budget | `target` | No budgets set | Set a monthly limit for a category and Finora will warn you before you overspend. | Set a limit → Categories |
| Goals | `piggy-bank` | No savings goals | Saving for a trip, a car or a rainy day? Create a goal and track your progress. | New goal → New goal sheet |

Flutter'da dashed border: `dotted_border` paketi yoki `CustomPainter`.

---

## 2. Goal details ekrani

Push. Bottom nav yo'q. Padding 8 20 28, gap 16.

```
Header: back (→ Budgets) · "Goal" 20/700 · trash tugma 44 (ikon trash-2 18 danger) → Delete sheet
Hero card (#064E3B, r24, padding 20, gap 16)
├ ikon 48 r15 #10B981 (24 #052E1F) · nom 18/600 + "Target date · Dec 2027" 13 #A7F3D0
│   [yetgan bo'lsa] badge h26 #10B981: check 14 + "Reached" 12/700 (fnPop)
├ "Saved" 13 #A7F3D0 · "12 000 000" 32/700 + " UZS" 15/500 · "of 30 000 000 UZS" 14 #D1FAE5
└ Progress h10 track #0B5E48 fill #10B981 (width tween 600ms)
    "40% saved" 13/600 oq ··· "18 000 000 UZS to go" 13 #A7F3D0
Grid 2 (gap 10): Add money (h52 r16 primary, plus 18) | Withdraw (h52 surface border, minus 18)
Info card (r20 padding 4 16):
├ calendar-clock · "Suggested monthly" / "To reach it by Dec 2027" ··· "1.2M UZS"
└ repeat · "Auto-save" / "1 000 000 UZS on the 1st of each month" | "Off" ··· Switch 44×24
"History" 17/600
├ [bo'sh] dashed karta: "No deposits yet. Add money to get started." 14 ink3
└ karta: qator ikon 40 r12 · "Deposit"/"Withdrawal" 15/500 + sana 13 ink3 ··· summa 15/600
```

### 2.1 Hisob-kitob

```dart
const months = {'Dec 2026':3,'Mar 2027':6,'Jun 2027':9,'Dec 2027':15,'Jun 2028':21};
final rem = max(target - saved, 0);
final perMonth = rem == 0 ? '—' : '${short((rem / (months[due] ?? 12) / 1000).ceil() * 1000)} UZS';
final pct = '${(min(saved / target, 1) * 100).round()}% saved';
final left = rem > 0 ? '${fmt(rem)} UZS to go' : 'Target reached';
```

History qatori: Deposit → ikon `arrow-down-left`, fon tint, summa `+1 000 000` primary. Withdrawal → `arrow-up-right`, fon background, summa `−400 000` ink. Stagger 40ms.

Auto-save switch: yoqilsa 1 000 000 UZS/oy → toast `Auto-save on · 1 000 000 UZS/month`; o'chsa `Auto-save off`. Switch: trek on `#10B981` / off `border`, knob 20 oq, soya, 250ms.

### 2.2 Add money / Withdraw sheet (`33-goal-add-money.png`)

```
Header: "Add money" | "Withdraw" 20/600 + goal nomi 13 ink2 · close
Amount (markaz): TextField 40/700 tabular, width 240, center, placeholder "0"
   ostida: "UZS" 14/500 ink3  yoki xato "Only 6 200 000 UZS available" danger
Quick grid 3 (gap 8): +100K · +500K · +1M (h40 r12 background 14/600) — qo'shib boradi
Account row (padding 12 14, r16, 1px border): karta mini 40×28 r7 #064E3B · "From"/"To" 15/500 + "Kapitalbank Uzcard •••• 4821" 13 ink3 · chevron-right
Button h56 r16: "Add to goal" | "Withdraw to card"
```

| Holat | Tugma |
|---|---|
| Add, summa > 0 | `#10B981` / `#052E1F` |
| Withdraw, 0 < summa ≤ saved | fon `ink`, matn `surface` |
| Summa 0 yoki withdraw > saved | `divider` / `ink3`, disabled |

Saqlash: history boshiga `[±summa, '28 Sep']`. Toast: `1 000 000 UZS added` / `… UZS withdrawn`; maqsadga yetsa `Goal reached!`.

### 2.3 Delete sheet (`34-goal-delete.png`)

- Ikon box 56 r18 `dangerSoft`, `trash-2` 24 danger.
- `Delete "Emergency fund"?` 20/600; `12 000 000 UZS will be returned to your main account.` 14/21 ink2.
- Grid 2: Cancel (h52 r16 background) | Delete (h52 r16 danger, oq matn) → Budgets, toast `Goal deleted`.

---

## 3. New goal sheet (`35-new-goal.png`)

```
Header "New goal" + close
Row: preview ikon 56 r18 #10B981 (26 #052E1F) · "Goal name" 13/600 ink2 + TextField h50 r14 1px border "e.g. New car, Wedding, Vacation" (max 32)
Icon picker grid 8 (gap 6), kvadrat aspect 1, r12:
   piggy-bank · plane · laptop · car · house · graduation-cap · heart · gift
   tanlangan: tint + 1.5px #10B981, ikon primary; oddiy: background + 1.5px shaffof, ikon ink2
"Target amount" + field h50 r14: TextField 17/600 tabular "0" + "UZS" 14/500 ink3
   [xato] 13/500 danger
"Target date" chiplar (scroll): Dec 2026 · Mar 2027 · Jun 2027 (default) · Dec 2027 · Jun 2028
   tanlangan: #10B981 / #052E1F; oddiy: shaffof, 1px border
"Monthly auto-save" segmented 4 (bg background): Off · 500K · 1M · 2M
   hint 13 ink2
Button "Create goal" h56 r16
```

Validatsiya (`Create goal` bosilganda):

| Shart | Xato matni | Border |
|---|---|---|
| nom bo'sh | Give your goal a name. | nom field 1.5px danger |
| target < 100 000 | Target must be at least 100 000 UZS. | summa field 1.5px danger |

Yaroqli bo'lsa tugma primary, aks holda `divider`/`ink3` (lekin bosilsa xatolar ko'rsatiladi).

Hint:
- target yo'q → `Enter a target to see your monthly plan.`
- auto-save bor → `At 1M/month you reach it in ~5 months.` (`ceil(target / auto)`)
- auto-save yo'q → `Save ~556K UZS/month to reach it by Jun 2027.`

Saqlash: `saved: 0, history: []`, ro'yxat oxiriga; toast `Goal created`.

---

## 4. Dark mode

`71-dark-budgets.png`. Hero goal kartasi va Goal hero ranglari dark'da ham o'zgarmaydi (`#064E3B`).
