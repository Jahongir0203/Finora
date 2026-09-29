# Finora — Activity, New transaction, Export, Scan

Versiya 1.0 · 28.09.2026 · Flutter (iOS / Android)

Bog'liq: `docs/DESIGN_SYSTEM.md` (tokenlar), `docs/screens/AUTH_SCREENS.md` (umumiy qoidalar), `docs/screens/HOME_NOTIFICATIONS.md` (bottom nav, toast).

Skrinshotlar (`docs/screenshots/`, 390×844 @2x):

| Fayl | Nima |
|---|---|
| `11-activity.png` | Activity, ma'lumotli |
| `11-activity-full.png` | Activity, to'liq uzunlik |
| `10-activity-empty.png` | Activity, yangi foydalanuvchi |
| `12-add-transaction.png` | New transaction sheet (150 000 kiritilgan) |
| `13-export-report.png` | Export report sheet — forma |
| `14-export-ready.png` | Export — "Report ready" |
| `15-scan-receipt.png` | Scan — Receipt rejimi |
| `16-scan-result.png` | Receipt scanned sheet |
| `17-scan-qr-error.png` | QR rejim — "No QR code found" |
| `70-dark-activity.png` | Activity, dark mode |

---

## 0. AI uchun ko'rsatma (prompt)

> Quyidagi spetsifikatsiya va skrinshotlar asosida Flutter kodini yoz.
> - Faqat `DESIGN_SYSTEM.md` tokenlari. Hardcode rang yo'q (faqat shu faylda aytilgan kategoriya ranglari).
> - Fayllar: `activity_screen.dart`, `transaction_tile.dart`, `day_group.dart`, `add_transaction_sheet.dart`, `amount_keypad.dart`, `category_chip.dart`, `export_sheet.dart`, `scan_screen.dart`, `scan_result_sheet.dart`, `scan_error_sheet.dart`.
> - Riverpod, `go_router`, `lucide_icons`, Onest, `camera` + `mobile_scanner` (QR), `share_plus`.
> - Summalar: bo'sh joy bilan (`12 500 000`), `FontFeature.tabularFigures()`. Minus belgisi `−` (U+2212).
> - Matnlarni o'zgartirma. Press effekti `scale 0.96`, 120ms.

---

## 1. Umumiy

| Parametr | Qiymat |
|---|---|
| Fon | `background` `#F4F7F5` (dark `#0B1210`) |
| Gorizontal padding | 20 |
| Bloklar orasidagi gap | 16 |
| Karta | `surface`, 1px `border`, radius 20 |
| Bottom nav | ko'rinadi (Activity tab aktiv) |
| Ekranga kirish animatsiyasi | `fnIn`: opacity 0→1 + translateY 12→0, 450ms, `Cubic(0.2,0.8,0.2,1)` |

### Kategoriyalar (umumiy ma'lumot, barcha ekranlar)

| id | Nomi | Lucide ikon | Rang | Default limit |
|---|---|---|---|---|
| groceries | Groceries | `shopping-cart` | `#10B981` | 2 500 000 |
| food | Food & drinks | `utensils` | `#F59E0B` | 800 000 |
| transport | Transport | `car` | `#3B82F6` | 600 000 |
| bills | Bills | `receipt` | `#8B5CF6` | — |
| health | Health | `heart-pulse` | `#EF4444` | — |
| shopping | Shopping | `shopping-bag` | `#EC4899` | 1 500 000 |
| housing | Housing | `house` | `#14B8A6` | — |
| subs | Subscriptions | `repeat` | `#6366F1` | — |
| salary (income) | Salary | `briefcase` | `#10B981` | — |
| transfer (income) | Transfer | `arrow-down-left` | `#0EA5E9` | — |

**Tint qoidasi:** ikon foni = kategoriya rangi + alpha `0x1F` (~12%). Masalan `#10B9811F`. Flutter: `color.withOpacity(0.12)`.

---

## 2. Activity ekrani

Skrinshot: `11-activity.png`, `11-activity-full.png`.

### 2.1 Tuzilma

```
Scaffold(bg: background)
└ SafeArea
  └ CustomScrollView (padding: 8 20 28)
    ├ Header row
    │   ├ Text "Activity" (24/700, letterSpacing -0.24)
    │   └ CircleIconButton 44 (surface, 1px border) → icon download 20
    ├ SearchField (h48, r14, surface, 1px border, padding 0 14)
    │   ├ icon search 18 ink3
    │   └ TextField "Search transactions" (15)
    ├ FilterChips row (gap 8): All · Expenses · Income
    ├ DayGroup × N
    │   ├ Row: label (13/600 ink2) ··· total (13 tabular ink2), padding 0 4
    │   └ Card (r20, padding 4 16) → TransactionTile × n
    └ EmptyState / NoResults (shartli)
BottomNav
```

### 2.2 Filter chip

| Holat | Fon | Matn | Border |
|---|---|---|---|
| Tanlangan | `ink` | `surface` | 1px `ink` |
| Oddiy | `surface` | `ink` | 1px `border` |

Balandlik 36, padding 0 16, radius 999, 14/500.

### 2.3 TransactionTile

| Element | Qiymat |
|---|---|
| Padding | vertikal 12, gap 12 |
| Ajratgich | birinchidan tashqari: yuqorida 1px `divider` |
| Ikon box | 44×44, r14, fon = tint, ikon 20 kategoriya rangi |
| Title | 15/500, 1 qator, ellipsis |
| Sub | `"{Category} · {HH:mm}"` 13 `ink3` |
| Summa | 15/600 tabular. Kirim: `+12 500 000` `primary` (`#047857`, dark `#34D399`). Chiqim: `−186 400` `ink` |
| Kirish | stagger: har element `delay = index × 40ms`, `fnIn` |

Sub matnida valyuta yo'q, faqat raqam.

### 2.4 Guruhlash

- Kalit: `Today`, `Yesterday`, keyin `Wed, 24 Sep` formati (`EEE, d MMM`).
- Guruh summasi = kirim − chiqim, `+12 313 600 UZS` yoki `−139 000 UZS`.

### 2.5 Qidiruv va filtr mantiqi

```dart
final q = query.trim().toLowerCase();
final list = txs.where((t) =>
  (filter == all || (filter == income ? t.amount > 0 : t.amount < 0)) &&
  (q.isEmpty || '${t.title} ${cat(t.cat).name}'.toLowerCase().contains(q)));
```

### 2.6 Holatlar

| Holat | Shart | UI |
|---|---|---|
| Ma'lumotli | `list.isNotEmpty` | guruhlar |
| Bo'sh (yangi foydalanuvchi) | `txs.isEmpty` | `10-activity-empty.png` |
| Natija yo'q | `txs.isNotEmpty && list.isEmpty` | "Nothing found" |

**Empty illyustratsiya (umumiy pattern, barcha ekranlarda):**
- Tashqi doira 96 (katta variant 120), `tint`, `fnPop` (scale 0.6→1, 600ms).
- Ichki kvadrat 60 (katta 68), r20 (katta r22), `#10B981`, ikon 28 (katta 30) `#052E1F`.
- Ichki kvadrat `fnFloat`: translateY 0 → −6 → 0, 3.5s, cheksiz.
- Sarlavha 18/700 (katta 20/700), matn 14/20 (katta 15/22) `ink2`, max-width 260–280, markazda.

| Holat | Ikon | Sarlavha | Matn | Tugmalar |
|---|---|---|---|---|
| Bo'sh | `receipt` | No transactions yet | Everything you add or scan will appear here, grouped by day. | `Add transaction` (primary, h44 r14) + `Scan receipt` (tint, `primary` matn) |
| Natija yo'q | `search-x` | Nothing found | No transactions match your search or filter. Try another word or category. | `Clear filters` (tint) → query = '', filter = all |

---

## 3. New transaction sheet

Skrinshot: `12-add-transaction.png`. Ochiladi: bottom nav markaziy `+`, Home "Add", empty state tugmalari, Scan → klaviatura ikoni.

### 3.1 Bottom sheet umumiy qoidasi (barcha sheetlar)

| Parametr | Qiymat |
|---|---|
| Overlay | `rgba(6,20,14,0.45)`, fade 300ms, tap → yopiladi |
| Sheet | `surface`, radius yuqori 28, padding 10 20 34, gap 16 |
| Handle | 40×5, r999, `border` rangi, markazda |
| Header | Title 20/600 + close tugma 40×40 doira `background` fonida, ikon `x` 18 |
| Kirish | `fnSheet`: translateY 100% → 0, 420ms, `Cubic(0.2,0.9,0.3,1)` |
| Max balandlik | 790 (uzun formalar scroll) |
| Flutter | `showModalBottomSheet(isScrollControlled: true, backgroundColor: transparent)` |

### 3.2 Tuzilma

```
Sheet
├ Handle
├ Header "New transaction" + close
├ Segmented (bg background, r14, padding 4, gap 4): Expense | Income  (h38 r10 14/600)
├ Amount (markaz, padding 6 0): "−150 000" 40/700 tabular + "UZS" 17/500 ink3
├ CategoryChips (gorizontal scroll, margin 0 -20, padding 0 20, gap 8)
├ Keypad 3×4 (gap 6): 1..9, 000, 0, ⌫(icon delete 22)
└ Save button h56 r16 "Save transaction"
```

### 3.3 Qoidalar

| Element | Qoida |
|---|---|
| Segment aktiv | fon `surface`, matn `ink`; nofaol: shaffof, `ink2` |
| Turi almashsa | Expense → default kategoriya `groceries`; Income → `salary` |
| Chip ro'yxati | Expense: 8 ta chiqim kategoriyasi. Income: Salary, Transfer |
| Chip | h38, padding 0 14, r999, ikon 16 + nom 14/500. Tanlangan: fon `ink`, matn/ikon `surface`. Oddiy: `surface`, 1px `border`, ikon kategoriya rangida |
| Summa rangi | bo'sh `0` → `ink4`; chiqim `ink`; kirim `primary` |
| Prefiks | chiqim `−`, kirim `+` (0 da prefiks yo'q) |
| Keypad tugma | h52, r14, 22/500. Bosilganda fon `background` |
| Maks uzunlik | 11 raqam |
| Save | `amount > 0` → `#10B981` / matn `#052E1F`; aks holda `divider` / `ink3`, bosilmaydi |

Save natijasi: tranzaksiya "Today" guruhiga, joriy vaqt bilan qo'shiladi; balans, income/expense yangilanadi; sheet yopiladi; toast `Transaction saved`.

---

## 4. Export report sheet

Skrinshotlar: `13-export-report.png`, `14-export-ready.png`. Ochiladi: Activity/Statistics header'dagi `download` tugmasi, Profile → Export data.

### 4.1 Uch bosqich

| Bosqich | UI |
|---|---|
| `form` | Forma (pastda) |
| `progress` | "Preparing your report…" + progress bar, 1.7s |
| `done` | "Report ready" + Share / Done |

### 4.2 Forma

```
Header "Export report" + close
Segmented 4 (bg border rangi): Daily | Weekly | Monthly | Yearly  (h36 13/600)
Range row (bg background, r14, padding 12 14): icon calendar 18 primary · range 15/600 · "{n} transactions" 13 ink3
Summary grid 3 ustun (gap 8): kartochka 1px border r14 padding 10
   Income  "+13M" primary | Expenses "−5.46M" ink | Net "+7.54M" (manfiy bo'lsa danger)
"Include" label 13/600 ink2 → chiplar (wrap, gap 8): Expenses, Income, Transfers
"Format" label → 3 ta kartochka h84 r16: PDF (file-text, "Report") · Excel (file-spreadsheet, ".xlsx") · CSV (file, "Raw data")
[xato] icon circle-alert 15 + "Select at least one type to export" 13/500 danger
Button h56 r16: icon download 18 + "Export PDF"
```

| Davr | Range | Soni | Income | Expense | Fayl nomi qismi |
|---|---|---|---|---|---|
| Daily | 28 Sep 2026 | 2 | 12 500 000 | 186 400 | 28sep2026 |
| Weekly | 22 – 28 Sep 2026 | 8 | 13 000 000 | 767 400 | w39_2026 |
| Monthly | September 2026 | 64 | 13 000 000 | 5 460 000 | sep2026 |
| Yearly | January – September 2026 | 712 | 117 000 000 | 52 900 000 | 2026 |

- Fayl: `finora_{period}_{part}.{pdf|xlsx|csv}` → `finora_monthly_sep2026.pdf`.
- Include chip tanlangan: fon `ink`, ikon `check`; tanlanmagan: `surface` + 1px border, ikonlar `arrow-up-right` / `arrow-down-left` / `arrow-left-right`.
- Include o'chirilgan tur summary'da 0 bo'ladi.
- Format tanlangan: fon `tint`, 1.5px `#10B981`, ikon `primary`. Oddiy: `surface`, 1.5px `border`, ikon `ink2`.
- Hech biri tanlanmasa: xato qatori ko'rinadi, tugma `divider`/`ink3`, bosilmaydi.
- Qisqa format (`short`): ≥1M → `5.46M` (oxirgi nollar olib tashlanadi), aks holda `186K`.

### 4.3 Progress

- Ikon box 76, r24, `tint`, ikon `file-text` 34, `fnFloat` 1.6s.
- "Preparing your report…" 18/600, ostida fayl nomi 13 `ink3`.
- Progress bar h8 r999 `divider`, ichida `#10B981` 0→100% 1.6s.

### 4.4 Done

- Doira 80 `#10B981`, ikon `check` 38 `#052E1F`, `fnPop` elastik (`Cubic(0.2,0.9,0.3,1.4)`), soya `0 12 30 rgba(16,185,129,.35)`.
- "Report ready" 20/700, ostida `finora_monthly_sep2026.pdf · 1.2 MB` (Excel 86 KB, CSV 24 KB).
- Grid 2: `Share` (h54, 1px border, ikon `share-2`) → `Share.shareXFiles`; `Done` (primary) → yopish.

---

## 5. Scan ekrani

Skrinshot: `15-scan-receipt.png`. Doim qorong'i, bottom nav yo'q.

| Parametr | Qiymat |
|---|---|
| Fon | `#0B0F0D`, status bar oq |
| Padding | 8 20 40, gap 18 |
| Header | close `x` (44 doira `#1F2925`) · "Scan" 17/600 markazda · flash tugma |
| Flash | o'chiq: `#1F2925` + `zap-off` oq; yoniq: `#10B981` + `zap` `#052E1F` |
| Rejim segmenti | fon `#1F2925` r14; aktiv `#FFFFFF`/`#0E1A14`, nofaol `#A7B3AC` — Receipt · QR payment |
| Kamera maydoni | flex, min 400, r28, `#18201C` — haqiqiy ilovada `CameraPreview` |
| Burchak ramkalar | 36×36, 4px `#10B981`, tashqi burchak radius 14, chetdan 40 |
| Skan chizig'i | 2px `#10B981`, glow `0 0 16 4 rgba(16,185,129,.55)`, chapdan/o'ngdan 44; `fnScan`: top 14% → 86% → 14%, 2.6s ease-in-out cheksiz |
| Hint | 14 `#A7B3AC`: Receipt → "Fit the whole receipt inside the frame"; QR → "Point the camera at a payment QR code" |
| Pastki qator | galereya (52 doira, `image`) · shutter 78 (4px `#10B981` halqa, ichi oq doira, padding 5) · qo'lda kiritish (52, `keyboard`) |

Prototipdagi qog'oz chek / QR rasm — faqat placeholder; Flutter'da kamera oqimi.

Harakatlar:
- Shutter (Receipt) → OCR → `Receipt scanned` sheet.
- Shutter (QR) topilmasa → `No QR code found` sheet.
- Keyboard → Home + New transaction sheet.

### 5.1 Receipt scanned sheet (`16-scan-result.png`)

```
Header: doira 28 #10B981 + check 16 · "Receipt scanned" 20/600 · close
Merchant box (bg background, r16, padding 12): ikon 44 r14 tint shopping-cart · "Korzinka · Chilonzor" 15/600 · "28 Sep 2026, 14:32" 13 ink2
Items: qator padding 8 0, 14; nom + miqdor (ink3) ··· narx tabular; ajratgich divider
Total: padding-top 12, yuqorida 1px dashed ink4, 17/600 "Total" ··· "186 400 UZS"
Category row: "Category" 14 ink2 ··· chip h34 tint primary "Groceries" (ikon 15)
Grid 1fr 2fr: Retake (h56, 1px border) | Save expense (primary)
```

Namuna qatorlar: Milk 1 L ×2 29 800 · Non bread ×3 12 000 · Chicken breast 1 kg 64 900 · Apples 1.5 kg 27 000 · Rice Lazer 2 kg 36 000 · Green tea ×1 16 700.

Save expense → tranzaksiya qo'shiladi, Home'ga qaytadi, toast `Expense saved`. Overlay bu sheetda `rgba(6,20,14,0.55)`.

### 5.2 No QR code found (`17-scan-qr-error.png`)

- Doira 80 `dangerSoft`, ikon `scan-line` 34 `danger`, `fnShake` (translateX ±6, 500ms).
- "No QR code found" 20/700; "Move closer and make sure the code is well lit and fully inside the frame." 15/22 `ink2`, max 290.
- `Try again` (h54 primary) → sheet yopiladi; `Enter manually` (h48, matn `primary`) → New transaction.

---

## 6. Dark mode

`70-dark-activity.png`. Tokenlar `DESIGN_SYSTEM.md` dark jadvalidan. Tanlangan filter chip: fon `ink` (`#E8EFEB`), matn `surface` (`#141D19`). Tint fonlar `withOpacity(0.12)` — dark'da ham shunday.
