"""Tashqi provayder ulanmaguncha ishlatiladigan lokal "model".

Real LLM provayderi faqat ma'lumotni o'qitishda ishlatmaslik sharti yozilgan shartnomadan
keyin ulanadi (02-backend.md, 8-bo'lim) — shu InsightsModel porti orqali.
Javob foydalanuvchi tilida (`language`), faqat jamlangan summalar asosida.
"""

import json

from app.core.i18n import format_amount, t


class RuleBasedInsightsModel:
    async def complete(self, system: str, prompt: str) -> str:
        data = json.loads(prompt)
        locale = str(data.get("language") or "uz-Latn")
        days = int(data.get("window_days", 90))
        totals: dict[str, int] = {}
        for cats in (data.get("expenses_by_month_and_category") or {}).values():
            for cat, amount in cats.items():
                totals[cat] = totals.get(cat, 0) + int(amount)
        if not totals:
            return t("ai.no_data", locale, days=days)
        total = sum(totals.values())
        top_cat, top_sum = max(totals.items(), key=lambda kv: kv[1])
        share = round(top_sum * 100 / total) if total else 0
        return t("ai.summary", locale, days=days, total=format_amount(total),
                 category=top_cat, share=share)
