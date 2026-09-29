# Finora — Empty va Error holatlari (umumiy)

Versiya 1.0 · 28.09.2026 · Flutter

Bitta qayta ishlatiladigan `StateView` vidjeti. Har ekran o'zining empty holatini (masalan Activity "No transactions yet") shu faylda yoki ekran faylida aytilgan matn bilan ko'rsatadi; to'liq ekranli holatlar (offline, server xatosi, sessiya) shu vidjet bilan.

Skrinshotlar: `60-states-empty.png`, `61-states-error.png`.

---

## 0. AI uchun ko'rsatma (prompt)

> `state_view.dart` yoz: `StateView({required StateKind kind, required IconData icon, required String title, required String body, String? primary, IconData? primaryIcon, String? secondary, VoidCallback? onPrimary, VoidCallback? onSecondary, bool busy = false})`. `kind`: `empty | error`. Quyidagi o'lcham va animatsiyalarga amal qil. Matnlarni o'zgartirma.

---

## 1. Tuzilma

```
Column (markaz, gap 22, padding 16 8, min-h 460)
├ Illustration 176×176 (Stack)
│   ├ tashqi doira (inset 0) — tint, opacity .55, fnBreath (scale 1 → 1.06 → 1, 3s cheksiz)
│   ├ ichki doira (inset 28) — tint
│   ├ markaz kvadrat 78×78 r24 — solid, soya 0 14 30 rgba(0,0,0,.14), ikon 34, fnFloat 3.5s
│   ├ nuqta 12px solid .6 (top 16, right 24), fnFloat 2.8s delay .4s
│   └ nuqta 8px solid .5 (bottom 28, left 14), fnFloat 3.2s delay .9s
├ Text (max 300, gap 8): title 22/700 letterSpacing −0.22 · body 15/22 ink2
└ Buttons (max 300, gap 8)
    ├ primary h52 r16 16/600: ikon 18 + label
    └ secondary h48 r16 15/600 primary rang (matnli)
```

| | Empty | Error |
|---|---|---|
| tint | `tint` `#ECFDF5` | `dangerSoft` `#FEF2F2` |
| solid | `#10B981` | `danger` `#DC2626` |
| markaz ikon rangi | `#052E1F` | `#FFFFFF` |
| primary tugma | `#10B981` / `#052E1F` | fon `ink` / matn `surface` |

**Busy (retry):** label `Trying…`, ikon `loader-circle` aylanadi (`fnRot` 800ms linear cheksiz), 1.4s dan keyin natija.

---

## 2. Empty holatlar

| Chip | Ikon | Title | Body | Primary | Secondary |
|---|---|---|---|---|---|
| No transactions | receipt | No transactions yet | Add your first expense or income and it will show up here. | Add transaction (plus) | Scan a receipt |
| No budgets | target | No budgets set | Set a monthly limit for a category and Finora will track it for you. | Create budget (plus) | — |
| No reminders | bell-ring | No payment reminders | Add bills, rent or subscriptions and we will remind you before they are due. | Add reminder (plus) | — |
| No alerts | check-check | You're all caught up | New alerts about budgets, payments and income will appear here. | — | — |
| No results | search-x | Nothing found | No transactions match "Evos cafe". Check the spelling or try a category name. | Clear search (x) | — |
| No stats | chart-pie | Not enough data yet | Statistics appear after you have at least a week of transactions. | Add transaction (plus) | — |

## 3. Error holatlar

| Chip | Ikon | Title | Body | Primary | Secondary |
|---|---|---|---|---|---|
| Offline | wifi-off | No internet connection | Check your Wi-Fi or mobile data and try again. Changes you make offline are saved. | Try again (refresh-cw) | — |
| Server | server-crash | Something went wrong | We could not load your data. This is on our side. Please try again in a moment. | Retry (refresh-cw) | Contact support |
| Bank sync | cloud-off | Bank sync failed | Kapitalbank did not respond. Transactions from this card may be missing. | Reconnect bank (link) | Remind me later |
| Scan | scan-line | Couldn't read the receipt | The photo is too dark or blurry. Hold the phone steady and keep the whole receipt in the frame. | Retake photo (camera) | Enter manually |
| Export | file-x | Export failed | The report could not be created. Free up some storage and try again. | Try again (refresh-cw) | — |
| Session | lock | Session expired | For your security we signed you out after 15 minutes of inactivity. | Sign in again (log-in) → Sign in | — |

Qachon ko'rsatiladi:
- **Offline** — `connectivity_plus` offline va keshlangan ma'lumot yo'q. Kesh bo'lsa Home'dagi offline banner (`HOME_NOTIFICATIONS.md`).
- **Server** — API 5xx / timeout.
- **Bank sync** — bank integratsiyasi xatosi (karta sahifasida yoki Home banner).
- **Scan** — OCR natija qaytarmasa.
- **Export** — fayl yaratish xatosi (Export sheet ichida `progress` o'rniga).
- **Session** — refresh token muddati o'tgan.

Prototipdagi "Empty & error states" ekrani (tablar + chiplar) faqat ko'rik uchun; ilovada alohida ekran sifatida kerak emas.
