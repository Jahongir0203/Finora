# Finora — Payment reminders, New reminder

Versiya 1.0 · 28.09.2026 · Flutter

Bog'liq: `docs/DESIGN_SYSTEM.md`, `docs/screens/ACTIVITY_SCAN.md` (kategoriyalar, sheet qoidalari), `docs/screens/HOME_NOTIFICATIONS.md` (Home'dagi "Upcoming payments").

Skrinshotlar: `41-reminders.png`, `40-reminders-empty.png`, `42-new-reminder.png`.

---

## 0. AI uchun ko'rsatma (prompt)

> Spetsifikatsiya va skrinshotlar asosida Flutter kodini yoz.
> - Fayllar: `reminders_screen.dart`, `reminder_tile.dart`, `date_badge.dart`, `new_reminder_sheet.dart`, `day_picker.dart`.
> - Model: `Reminder {id, title, categoryId, amount, dueDate, repeat (once|weekly|monthly|yearly), notify (sameDay|dayBefore|threeDaysBefore), enabled}`.
> - Lokal bildirishnoma: `flutter_local_notifications`, `notify` bo'yicha rejalashtiriladi; `enabled=false` bo'lsa bekor qilinadi.
> - Matnlarni o'zgartirma.

---

## 1. Payment reminders ekrani

Push (Home quick action "Reminders", Home "Upcoming payments", Profile, notification). Bottom nav yo'q. Padding 8 20 28, gap 16.

```
Header: back · "Payment reminders" 17/600 · add tugma 44 doira #10B981 (plus 22 #052E1F) → New reminder
Summary card (#064E3B, r24, padding 20, gap 6)
├ "DUE IN THE NEXT 30 DAYS" 12/600 uppercase #A7F3D0
├ "4 991 000" 30/700 tabular oq + " UZS" 15/500 #A7F3D0
└ "4 payments scheduled" 14 #A7F3D0
[bo'sh] DashedEmptyCard
"Upcoming" 13/600 ink2
ReminderTile × n (gap 10)
```

Summary: faqat `enabled && dueIn <= 30` bo'lganlar yig'indisi va soni.

### 1.1 ReminderTile

Karta surface, 1px border, r20, padding 14 16, gap 12, `fnIn` stagger 60ms.

| Element | Qiymat |
|---|---|
| DateBadge | 50×50 r14; oy 11/600 uppercase, kun 18/700 (line-height 20) |
| Title | 15/600, 1 qator ellipsis |
| Sub | `"142 000 UZS · Monthly"` 13 ink2 tabular |
| Due | 12/600 |
| Switch | 48×28, padding 3, knob 22 oq soyali; on `#10B981`, off `border` |

DateBadge ranglari:

| Holat | Fon | Matn |
|---|---|---|
| O'chiq | background | ink3 |
| dueIn ≤ 1 | warnSoft `#FEF3C7` | warn `#B45309` |
| Boshqa | tint | primary |

Due matni:

| dueIn | Matn | Rang |
|---|---|---|
| 0 | Due today | danger |
| 1 | Due tomorrow | warn |
| 2–14 | In 7 days | ink2 |
| >14 | 15 Nov | ink3 |
| o'chiq | Paused | ink3 (title ham ink3) |

Namuna ma'lumot:

| Title | Kategoriya | Summa | Sana | Repeat | On |
|---|---|---|---|---|---|
| Electricity | bills | 142 000 | 29 Sep | Monthly | ✓ |
| Internet · Uzonline | subs | 99 000 | 1 Oct | Monthly | ✓ |
| Rent | housing | 4 500 000 | 5 Oct | Monthly | ✓ |
| Gym membership | health | 250 000 | 10 Oct | Monthly | ✗ |
| Car insurance | transport | 1 200 000 | 15 Nov | Yearly | ✓ |

Ro'yxat `dueIn` bo'yicha o'sish tartibida.

### 1.2 Bo'sh holat (`40-reminders-empty.png`)

DashedEmptyCard: ikon `bell-ring`, "No payment reminders", "Add bills, rent or subscriptions and we will remind you before they are due.", tugma "Add reminder" → sheet. "Upcoming" sarlavhasi yashirin.

---

## 2. New reminder sheet (`42-new-reminder.png`)

Max balandlik 790, scroll.

```
Header "New reminder" + close
"Payment name" 13/600 ink2 + TextField h50 r14 1px border "e.g. Internet, Rent, Netflix"
"Amount" + field h50: TextField 17/600 tabular "0" + "UZS"
Category chips (scroll): Bills · Housing · Subscriptions · Transport · Health   (default Bills)
"Due date" → DayPicker (scroll, gap 8): 14 kun bugundan
   kartochka 52×64 r14: hafta kuni 11/500 ("Today" birinchisi) + kun 18/700
   tanlangan: fon ink, matn surface; oddiy: surface, 1px border. Default: 4-kun (index 3)
"Repeat" segmented 4 (bg background): Once · Weekly · Monthly (default) · Yearly
"Notify me" segmented 3: Same day · 1 day before (default) · 3 days before
Button "Save reminder" h56 r16
```

- Chip uslubi New transaction bilan bir xil (tanlangan fon `ink`).
- Segment: h36 r10 13/600; aktiv surface/ink, nofaol shaffof/ink2.
- Yaroqli: `title.trim().isNotEmpty && amount > 0` → primary tugma, aks holda `divider`/`ink3` disabled.
- Summa inputi faqat raqam, max 11, ko'rsatishda bo'sh joy bilan formatlanadi.
- Saqlash: `enabled: true`, ro'yxat `dueIn` bo'yicha qayta tartiblanadi, forma defaultga qaytadi, toast `Reminder set`.
