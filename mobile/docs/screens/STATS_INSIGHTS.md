# Finora — Statistics, AI insights

Versiya 1.0 · 28.09.2026 · Flutter

Bog'liq: `docs/DESIGN_SYSTEM.md`, `docs/screens/ACTIVITY_SCAN.md` (kategoriyalar jadvali, sheet qoidalari, empty pattern, Export sheet).

Skrinshotlar (`docs/screenshots/`):

| Fayl | Nima |
|---|---|
| `21-statistics.png` / `21-statistics-full.png` | Statistics (Month) |
| `20-stats-empty.png` | Yangi foydalanuvchi |
| `22-ai-insights.png` / `22-ai-insights-full.png` | AI insights |
| `23-ai-answer.png` | Savolga javob chiqqan holat |

---

## 0. AI uchun ko'rsatma (prompt)

> Spetsifikatsiya va skrinshotlar asosida Flutter kodini yoz.
> - Fayllar: `statistics_screen.dart`, `period_segmented.dart`, `category_donut.dart` (CustomPainter), `category_breakdown_list.dart`, `spending_trend_chart.dart`, `insights_screen.dart`, `ai_chat_card.dart`, `recommendation_card.dart`.
> - Grafik uchun tashqi kutubxona shart emas: donut va ustunlar `CustomPainter`/`AnimatedContainer` bilan. `fl_chart` ishlatsang ham o'lchamlar shu faylga mos bo'lsin.
> - AI javobi backend'dan (`POST /ai/ask`) keladi; prototipdagi javoblar — mock.
> - Matnlarni o'zgartirma.

---

## 1. Statistics ekrani

Bottom nav'da "Stats" tab. Padding 8 20 28, gap 16.

### 1.1 Tuzilma

```
Header row (gap 8)
├ "Statistics" 24/700 (flex)
├ Pill button h44 padding 0 14 r999 tint: icon sparkles 16 + "AI tips" 14/600 primary → AI insights
└ Circle 44 surface 1px border: icon download 20 → Export sheet
Period segmented (grid 3, bg border, r14, padding 4): Week | Month | Year  (h36 r10 14/600)
Donut card (r24, padding 20, gap 20, markazda)
├ Donut 200×200, ichki doira 144 surface
│   "SPENT" 12/600 letterSpacing .06em uppercase ink3 · "5.3M" 22/700 tabular · "UZS" 12 ink2
└ Breakdown list: qator padding 10 0
     ikon 36 r12 tint · nom 15/500 (flex) · foiz 13 ink3 (w40, o'ngga) · summa 15/600 tabular (w96, o'ngga)
Trend card (r24, padding 20, gap 16)
├ "Spending trend" 17/600 ··· icon trending-down 16 + "8% vs last" 13/600 primary
└ Bars h150, gap 6: ustun max-width 28, r8, label 11 ink3 ostida
```

### 1.2 Ma'lumot (oylik baza)

| Kategoriya | Summa | Foiz |
|---|---|---|
| Groceries | 1 840 000 | 35% |
| Shopping | 1 150 000 | 22% |
| Food & drinks | 920 000 | 17% |
| Bills | 610 000 | 12% |
| Transport | 460 000 | 9% |
| Health | 320 000 | 6% |

Koeffitsient: Week ×0.22, Month ×1, Year ×11.4 (1000 ga yaxlitlanadi). Jami `short()` formatida markazda.

Trend ustunlari:

| Davr | Label: qiymat |
|---|---|
| Week | M 180 · T 95 · W 240 · T 60 · F 310 · S 420 · S 150 |
| Month | W1 1200 · W2 1600 · W3 1100 · W4 1560 |
| Year | J F M A M J J A S O N D (S = 5.46, O–D = 0) |

- Balandlik: `max(v / max × 118, 4)` px.
- Rang: joriy davr ustuni (Week/Month — oxirgisi, Year — Sentyabr) `#10B981`; boshqalar `tint2` (`#D1FAE5`); 0 qiymat `divider`.

### 1.3 Donut

- Segmentlar ketma-ketligi jadval tartibida, soat yo'nalishida, yuqoridan (−90°) boshlanadi, oraliqsiz.
- Flutter: `CustomPainter`, `drawArc` stroke kengligi 28 (200−144)/2, `StrokeCap.butt`.
- Animatsiya `fnSpin`: rotate −90° + scale 0.85 → 0°/1, opacity 0→1, 900ms `Cubic(0.2,0.8,0.2,1)`.
- Davr almashsa: segmentlar 500ms tween.

### 1.4 Animatsiyalar

| Element | Animatsiya |
|---|---|
| Breakdown qatorlari | `fnIn`, stagger 50ms |
| Ustunlar | `fnCol`: scaleY 0→1 (pastdan), 700ms, stagger 40ms; davr almashsa height 500ms |
| Segmented | fon almashishi 200ms |

### 1.5 Empty holat (`20-stats-empty.png`)

Shart: yangi foydalanuvchi (kamida ~1 hafta ma'lumot yo'q). Period segmenti, kartalar yashirin.

- Doira 120: `conic-gradient(tint2 0–35%, divider 35–60%, tint 60–100%)`, ichki doira 84 `background`, ikon `chart-pie` 30 `primary`. `fnPop`.
- "Not enough data yet" 18/700.
- "Charts and category breakdowns appear after about a week of tracking." 14/20 `ink2`, max 270.
- `Add transaction` h44 r14 primary.

---

## 2. AI insights ekrani

Push (`fnPush`: translateX 24→0 + fade, 420ms). Bottom nav yo'q. Padding 8 20 28, gap 16.

### 2.1 Tuzilma

```
Header: back chevron-left (44 doira surface border) · "AI insights" 17/600 · badge h28 tint: sparkles 14 + "Beta" 12/600
Hero card (#064E3B, r24, padding 20, gap 8, overflow clip)
├ dekor doira 170 #10B981 opacity .18 (right -40, top -50), fnFloat 5s
├ "POTENTIAL SAVINGS THIS MONTH" 12/600 uppercase #A7F3D0
├ "1 240 000" 32/700 tabular oq + " UZS" 15/500 #A7F3D0
└ "Based on your last 90 days of transactions · 5 tips" 14/20 #A7F3D0
Chat card (surface, 1px border, r20, padding 14, gap 12)
├ icon message-circle 18 primary + "Ask Finora AI" 15/600
├ Suggestion chips (gorizontal scroll, gap 8): h34 padding 0 12 r999 tint primary 13/500
├ [javob bo'lsa] Dialog
│   ├ User bubble (o'ngda, max 80%): #10B981, matn #052E1F, r 16 16 4 16, padding 10 12, 14/20
│   └ AI qator: avatar 28 r9 #064E3B + sparkles 14 #A7F3D0
│        loading: bubble background r 16 16 16 4, 3 nuqta 7px ink3 (fnDot, 1s, delay 0/.15/.3s)
│        done: bubble background, 14/21, fnFade 400ms
└ Input h46 r14 background: TextField "Ask about your spending" + send 36 r10 #10B981 (arrow-up 18)
"Recommendations" 13/600 ink2
RecommendationCard × n (surface, border, r20, padding 16, gap 12)
├ ikon 40 r12 tint · title 15/600 · body 14/20 ink2
└ Actions row: savings badge h28 tint "−380 000" 12/700 · spacer · Dismiss (h36, ink2) · Action (h36 r12 fon ink, matn surface 14/600)
[bo'sh] "You're all set" empty
Disclaimer 12/18 ink3 markazda
```

### 2.2 Tavsiyalar (mock)

| id | Ikon / rang | Title | Tejash | Action |
|---|---|---|---|---|
| food | `utensils` `#F59E0B` | Cook at home more often | 380 000 | Set budget |
| taxi | `car` `#3B82F6` | Take the metro on weekdays | 300 000 | Set budget |
| groc | `shopping-cart` `#10B981` | Shop on discount days | 150 000 | Remind me |
| subs | `repeat` `#6366F1` | Overlapping subscriptions | 89 000 | Review |
| auto | `piggy-bank` `#0EA5E9` | Automate your savings | — (badge yo'q) | Turn on |

Body matnlari prototipda (`Finora App.dc.html`, `REC`) — so'zma-so'z ko'chir.

- Potential = ko'rinib turgan tavsiyalar tejashi yig'indisi + 321 000 (backend qiymati).
- Dismiss → karta yo'qoladi (`AnimatedList`, fade+size 250ms).
- Action → karta yo'qoladi + toast: Remind me → `Reminder set for Tuesdays`; Turn on → `Auto-save turned on`; qolgan → `Done. We will track it for you`.
- Hammasi yopilsa: empty — ikon `check-check`, "You're all set", "No new recommendations. We'll let you know when we spot a way to save.", tugma `Show dismissed`.
- Kartalar `fnIn`, stagger 70ms.

### 2.3 Chat mantiqi

```dart
Future<void> ask(String q) async {
  if (q.trim().isEmpty) return;
  state = state.copyWith(asked: q, loading: true, answer: '', input: '');
  final a = await api.ask(q);            // ~1.4s
  state = state.copyWith(loading: false, answer: a);
}
```

Tayyor savollar: `Where do I overspend?`, `How much can I save?`, `Compare with last month`. Enter yoki send tugmasi → `ask`. Faqat oxirgi savol-javob ko'rsatiladi.

Disclaimer: "AI suggestions are estimates based on your history, not financial advice."
