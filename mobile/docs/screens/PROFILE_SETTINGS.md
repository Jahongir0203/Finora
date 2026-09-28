# Finora — Profile, Security, Accounts & cards, Categories, Language, Currency, Help

Versiya 1.0 · 28.09.2026 · Flutter

Bog'liq: `docs/DESIGN_SYSTEM.md`, `docs/screens/ACTIVITY_SCAN.md` (kategoriyalar, sheet qoidalari, empty pattern), `docs/screens/PIN_SETUP_SCREENS.md` (Auto-lock, Change PIN mantiqi).

Skrinshotlar (`docs/screenshots/`):

| Fayl | Nima |
|---|---|
| `50-profile.png` / `50-profile-full.png` | Profile |
| `51-security-sheet.png` | Security sheet |
| `52-accounts-cards.png` / `52-accounts-cards-full.png` | Accounts & cards |
| `53-categories.png` | Categories |
| `54-category-edit.png` | Edit category sheet |
| `55-category-new.png` | New category sheet |
| `56-language.png` | Language |
| `57-currency.png` | Primary currency |
| `58-help-support.png` / `58-help-support-full.png` | Help & support (FAQ ochiq) |
| `72-dark-profile.png` | Dark mode |

---

## 0. AI uchun ko'rsatma (prompt)

> Spetsifikatsiya va skrinshotlar asosida Flutter kodini yoz.
> - Fayllar: `profile_screen.dart`, `settings_tile.dart`, `security_sheet.dart`, `accounts_screen.dart`, `bank_card_carousel.dart`, `categories_screen.dart`, `category_sheet.dart`, `language_screen.dart`, `currency_screen.dart`, `help_screen.dart`, `faq_tile.dart`, `radio_dot.dart`.
> - Hamma ichki ekranlar push (`fnPush`), bottom nav yo'q, back → Profile (Profile'ning o'zi → Home).
> - Til: `flutter_localizations` + ARB; tanlangan til `SharedPreferences`'da.
> - Matnlarni o'zgartirma.

---

## 1. Umumiy ichki ekran shabloni

```
Padding 8 20 28, gap 16
Header row (gap 12): back 44 doira (surface, 1px border, chevron-left 20) · title 17/600 (flex) · [ixtiyoriy o'ng tugma]
```

O'ng "+" tugma: 44 doira `#10B981`, ikon `plus` 22 `#052E1F`.

**Ro'yxat kartasi:** surface, 1px border, r20, padding 0 16 (yoki 4 16); qatorlar orasida 1px `divider` (birinchidan tashqari).

**RadioDot:** 22×22 doira, 2px halqa (tanlangan `#10B981`, oddiy `ink4`), ichida 10px `#10B981` nuqta scale 0↔1.

---

## 2. Profile (`50-profile.png`)

Padding 8 20 28, gap 20.

```
Header: back → Home · "Profile" 17/600
Avatar blok (markaz, padding 8 0, gap 10)
├ doira 88 tint2, "DK" 30/700 primary
├ "Doston Karimov" 20/600
└ "+998 90 123 45 67" 14 ink2
Settings card (padding 4 16) — qator h56:
   ikon box 36 r12 tint (ikon 18 primary) · label 15/500 (flex) · value 14 ink3 · chevron-right 18 ink3
   + oxirgi qator "Dark mode" — chevron o'rniga Switch 48×28
Log out tugma h52 r16 dangerSoft: log-out 18 + "Log out" 16/600 danger → Sign in
```

| Ikon | Label | Value | Harakat |
|---|---|---|---|
| wallet | Accounts & cards | 4 | Accounts |
| shapes | Categories | 10 (jami soni) | Categories |
| bell-ring | Payment reminders | yoqilganlar soni | Reminders |
| download | Export data | — | Export sheet |
| coins | Primary currency | UZS | Currency |
| globe | Language | English | Language |
| bell | Notifications | On | Notifications |
| shield-check | Security | Auto-lock 1 min | Security sheet |
| circle-help | Help & support | — | Help |
| moon | Dark mode | switch | tema almashadi (darhol) |

---

## 3. Security sheet (`51-security-sheet.png`)

```
Header "Security" + close
"Auto-lock" 15/600 + "Ask for PIN after the app is inactive for" 13 ink2
Segmented 3 (bg background, r14, padding 4): 1 min · 3 min · 5 min
   h40 r10 14/600; aktiv surface + soya 0 1 3 rgba(0,0,0,.08), matn ink; nofaol ink3
Timer qatori: icon timer 14 + "Locks in 0:45 without a tap" 13 ink3 (har soniyada yangilanadi)
Group (bg background, r18, padding 4 14):
├ h56: scan-face 20 primary · "Unlock with Face ID" 15/500 · Switch 44×24
└ h56 (yuqorida 1px border): key-round 20 · "Change PIN" · chevron-right → Create PIN (change rejimi)
Button h52 r16 fon ink, matn surface: lock 18 + "Lock now" → PIN lock
```

Tanlov → toast `Auto-lock set to 3 min`, taymer qayta boshlanadi. Mantiq to'liq: `PIN_SETUP_SCREENS.md`.

---

## 4. Accounts & cards (`52-accounts-cards.png`)

Padding 8 0 28 (gorizontal padding faqat ichki bloklarda 20), gap 18.

```
Header: back · "Accounts & cards" · + (→ karta qo'shish)
Total: "Total across 4 accounts" 13 ink2 · "24 850 000" 30/700 tabular + " UZS" 15/500 ink3
Card carousel (PageView / ListView snap, gap 12, padding 0 20)
Dots (markaz, gap 6): aktiv 18×6 #10B981, boshqa 6×6 ink4, 300ms
Actions grid 3 (gap 8, padding 0 20): kartochka h72 r18 surface border — ikon 20 + label 13/500
Details card (margin 0 20, padding 0 16): qator h50 14 — kalit ink2 ··· qiymat 600 tabular
"All accounts" 13/600 ink2
Accounts list card: ikon box 44 r14 (fon = karta rangi, ikon oq 20) · nom 15/500 + sub 13 ink3 ··· balans 15/600
Dashed tugma h52 r16 1.5px dashed ink4: plus 18 + "Add card or account" 15/600 primary
```

### 4.1 Bank kartasi

| Parametr | Qiymat |
|---|---|
| O'lcham | 290×180, r24, padding 20, oq matn, snap start |
| Dekor | doira 220 `rgba(255,255,255,.07)` (right −60, top −70); doira 160 `.05` (right 40, bottom −100) |
| Yuqori | bank nomi 15/600 ··· network badge 12/700 letterSpacing .08em, padding 4 8, r8, `rgba(255,255,255,.14)` |
| O'rta | "Balance" / "Frozen" 12 `rgba(255,255,255,.72)` · balans 24/700 + " UZS" 13/500 |
| Past | `•••• 4821` 15/500 letterSpacing .08em ··· `08/29` 13 |
| Muzlatilgan | opacity 0.55, label "Frozen" |
| Kirish | `fnPush`, stagger 90ms |

| Bank | Network | Balans | Last4 | Exp | Fon | Limit |
|---|---|---|---|---|---|---|
| Kapitalbank | UZCARD | 14 250 000 | 4821 | 08/29 | `#064E3B` | 10 000 000 UZS |
| Hamkorbank | HUMO | 5 400 000 | 7730 | 11/28 | `#1E293B` | 5 000 000 UZS |
| TBC Bank | VISA | 4 000 000 | 1094 | 03/30 | `#4C1D95` | 8 000 000 UZS |

Aktiv karta indeksi: `round(scrollOffset / 302)` (290 + 12).

### 4.2 Actions va Details (aktiv kartaga bog'liq)

| Action | Ikon / rang | Harakat |
|---|---|---|
| Top up | plus / primary | toast `Top up: choose a source` |
| Transfer | send / primary | Home + New transaction sheet |
| Freeze ↔ Unfreeze | snowflake / `#3B82F6` | holat almashadi, toast `Card frozen` / `Card unfrozen` |

Details: Card holder `DOSTON KARIMOV` · Card number `•••• 4821` · Status `Active` (primary) / `Frozen` (`#3B82F6`) · Monthly limit.

All accounts: 3 karta (`credit-card`) + Cash (`wallet`, `#B45309`, "Updated today", 1 200 000). Birinchi sub: `•••• 4821 · Main`.

---

## 5. Categories (`53-categories.png`)

```
Header: back · "Categories" · + → New category
Segmented 2 (bg border): Expenses | Income   (h36 13/600)
List card: qator h68 — ikon 44 r14 tint · nom 15/600 + sub 13 ink3 tabular · chevron-right
[bo'sh] empty: shapes, "No categories", "Create a category to group your transactions and set a budget.", "Add category"
Izoh 13 ink3 markaz: "Tap a category to change its name, icon, color or budget."
```

Sub: `Budget 2 500 000 · 1 transactions` (limit bo'lmasa faqat `{n} transactions`). Qatorlar `fnIn` stagger 40ms.

### 5.1 Category sheet (`54-category-edit.png`, `55-category-new.png`)

```
Header: "Edit category" | "New category" + close
Preview (markaz, gap 10): box 72 r22 (fon = rang + 1F), ikon 32 rangda, fnPop · nom 17/600 (bo'sh bo'lsa "Category name")
"Name" + field h50 r14 "e.g. Coffee"
"Icon" grid 6 (gap 8): tugma h46 r14 — 18 ta ikon
   tanlangan: fon rang+1F, 1.5px rang, ikon rangda; oddiy: background, ikon ink2
"Color" (wrap, gap 12): doira 32; tanlangan halqa: 0 0 0 3px surface, 0 0 0 5px rang (200ms)
[faqat Expense] "Monthly budget" field h50 "No limit" + "UZS"
[xato] circle-alert 15 + "Give the category a name" 13/500 danger
Edit: grid 1fr 2fr — Delete (h56 dangerSoft, danger) | Save changes (primary)
New: "Create category" (h56 primary)
```

Ikonlar: shopping-cart, utensils, coffee, car, bus, receipt, heart-pulse, dumbbell, shopping-bag, house, repeat, plane, graduation-cap, gift, baby, paw-print, smartphone, briefcase.

Ranglar: `#10B981 #14B8A6 #0EA5E9 #3B82F6 #6366F1 #8B5CF6 #EC4899 #EF4444 #F59E0B #84CC16`.

New default: ikon `coffee`, rang `#14B8A6`, tur = joriy tab. Toastlar: `Category added` / `Category updated` / `Category deleted`.

---

## 6. Language (`56-language.png`)

```
Header: back · "Language"
Izoh 14/20 ink2: "Menus, notifications and reports will use this language."
List card: qator h64 — kod box 40 r12 tint (13/700 primary) · nom 15/600 + sub 13 ink3 · RadioDot
```

| Kod | Nom | Sub |
|---|---|---|
| EN | English | English |
| UZ | O'zbekcha | Uzbek · Latin |
| ЎЗ | Ўзбекча | Uzbek · Cyrillic |
| RU | Русский | Russian |
| KZ | Қазақша | Kazakh |
| TR | Türkçe | Turkish |

Tanlash → darhol qo'llanadi, toast `Language set to Русский`. Qatorlar stagger 40ms.

---

## 7. Primary currency (`57-currency.png`)

```
Header: back · "Primary currency"
Search field h48 r14: search 18 + "Search currency"
List card: qator h64 — belgi doira 44 tint (14/700 primary) · kod 15/600 + nom 13 ink3 · kurs 13 ink3 · RadioDot
[topilmasa] empty: search-x, "No currency found", "Try a currency code like USD or a name like euro."
Izoh 13/19 ink3: "Rates update daily. Past transactions keep the rate from the day they were made."
```

| Kod | Belgi | Nom | Kurs |
|---|---|---|---|
| UZS | so'm | Uzbek so'm | Base |
| USD | $ | US dollar | 12 650 UZS |
| EUR | € | Euro | 14 120 UZS |
| RUB | ₽ | Russian ruble | 152 UZS |
| KZT | ₸ | Kazakhstani tenge | 25 UZS |
| GBP | £ | British pound | 16 900 UZS |
| CNY | ¥ | Chinese yuan | 1 760 UZS |
| TRY | ₺ | Turkish lira | 330 UZS |

Qidiruv: `"$code $name".toLowerCase().contains(q)`. Kurslar backend'dan (`GET /rates`). Toast `Primary currency: USD`.

---

## 8. Help & support (`58-help-support.png`)

```
Header: back · "Help & support"
Hero (#064E3B, r24, padding 20, gap 14): "How can we help?" 20/600 oq + search h48 r14 #0B5E48 (ikon #A7F3D0, "Search questions", matn oq)
Contacts grid 2 (gap 10): kartochka surface border r20 padding 14 — ikon 40 r12 tint · title 15/600 · sub 12 ink3 ellipsis
"Frequently asked" 13/600 ink2
FAQ card: savol qatori min-h56 — savol 15/500 · chevron-down 18 (ochiq: rotate 180°, 300ms)
   javob: AnimatedSize/ExpansionTile 350ms, 14/21 ink2, padding-bottom 14
[topilmasa] empty: search-x, "No matching questions", "Try other words or contact us directly. We reply within a few minutes.", "Start live chat"
"Finora 1.0.0 (128)" 13 ink3 markaz (package_info_plus)
```

| Ikon | Rang | Title | Sub | Harakat |
|---|---|---|---|---|
| message-circle | `#10B981` | Live chat | Replies in ~2 min | chat |
| send | `#0EA5E9` | Telegram | @finora_support | `url_launcher` t.me |
| phone | `#8B5CF6` | Call us | +998 71 200 00 00 | `tel:` |
| mail | `#F59E0B` | Email | help@finora.uz | `mailto:` |

FAQ (bir vaqtda bittasi ochiq; qidiruv savol+javob bo'yicha, qidirganda hammasi yopiladi):
1. How do I add a card?
2. Is my data safe?
3. How do payment reminders work?
4. How do I export my transactions?
5. Can I change my primary currency?

Javob matnlari prototipda (`faqs`) — so'zma-so'z ko'chir.

---

## 9. Dark mode

`72-dark-profile.png`. Faqat tokenlar almashadi; hero bloklar (`#064E3B`) va bank kartalari ranglari o'zgarmaydi.
