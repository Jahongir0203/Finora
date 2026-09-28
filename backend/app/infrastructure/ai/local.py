"""Tashqi provayder ulanmaguncha ishlatiladigan lokal "model".

Real LLM provayderi faqat ma'lumotni o'qitishda ishlatmaslik sharti yozilgan shartnomadan
keyin ulanadi (02-backend.md, 8-bo'lim) — shu InsightsModel porti orqali.
"""

import json


def _fmt(amount: int) -> str:
    return f"{amount:,}".replace(",", " ")


class RuleBasedInsightsModel:
    async def complete(self, system: str, prompt: str) -> str:
        data = json.loads(prompt)
        totals: dict[str, int] = data.get("expenses_by_category", {})
        if not totals:
            return "Oxirgi davrda xarajatlar topilmadi. Tranzaksiyalarni kiritishni boshlang."
        total = sum(totals.values())
        top_cat, top_sum = max(totals.items(), key=lambda kv: kv[1])
        share = round(top_sum * 100 / total) if total else 0
        return (
            f"Oxirgi {data.get('period_days', 30)} kunda jami xarajat {_fmt(total)} so'm. "
            f"Eng katta ulush: {top_cat} ({share}%). "
            f"Shu kategoriya uchun oylik byudjet belgilashni ko'rib chiqing."
        )
