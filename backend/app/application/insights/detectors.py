"""Qoidaga asoslangan tavsiya detektorlari (BE-901). Har kuni tunda + so'rovda (6 soat kesh).

Barcha summalar so'mda, 1000 ga yaxlitlanadi. Detektorlar faqat jamlangan ma'lumot bilan
ishlaydi — LLM kerak emas.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, tzinfo
from typing import Any
from uuid import UUID

from app.application.common.uow import UnitOfWork
from app.domain.common.ids import uuid7
from app.domain.common.time import add_months, local_midnight, month_key, month_start
from app.domain.insights.entities import Insight, InsightAction, InsightKind
from app.domain.transactions.entities import Transaction, TransactionType
from app.domain.transactions.repository import TransactionFilter

OVERSPEND_RATIO = 1.2
MIN_OVERSPEND = 100_000
DISCOUNT_MIN_TRIPS = 8
DISCOUNT_SAVING_RATE = 0.05
AUTOSAVE_RATE = 0.10
SCAN_LIMIT = 50_000


def round_k(value: float) -> int:
    return round(value / 1000.0) * 1000


def _normalize(title: str | None) -> str:
    return " ".join((title or "").casefold().split())


@dataclass(slots=True)
class Draft:
    kind: InsightKind
    action: InsightAction
    icon: str
    saving: int
    key: str
    params: dict[str, Any]
    category_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


async def detect(uow: UnitOfWork, user_id: UUID, now: datetime, tz: tzinfo,
                 limits: dict[str, int | None]) -> list[Draft]:
    today = now.astimezone(tz).date()
    this_month = month_start(today)
    three_back = add_months(this_month, -3)
    rows = await uow.transactions.list_for_user(
        user_id, TransactionFilter(types=(TransactionType.EXPENSE, TransactionType.INCOME),
                                   since=local_midnight(three_back, tz)),
        limit=SCAN_LIMIT)
    drafts: list[Draft] = []
    period = month_key(today)

    def local(tx: Transaction) -> date:
        return tx.occurred_at.astimezone(tz).date()

    expenses = [r for r in rows if r.type is TransactionType.EXPENSE]
    mtd: dict[str, int] = defaultdict(int)
    past: dict[str, int] = defaultdict(int)
    for r in expenses:
        (mtd if local(r) >= this_month else past)[r.category_id] += r.amount

    # 1. Kategoriya 3 oylik o'rtachadan > 20% yuqori
    for cat, spent in mtd.items():
        avg = past.get(cat, 0) / 3
        if avg <= 0 or spent < MIN_OVERSPEND or spent <= avg * OVERSPEND_RATIO:
            continue
        has_limit = bool(limits.get(cat))
        drafts.append(Draft(
            kind=InsightKind.OVERSPEND,
            action=InsightAction.REVIEW if has_limit else InsightAction.SET_BUDGET,
            icon="trending-up", saving=round_k(spent - avg), key=f"overspend:{cat}:{period}",
            params={"category_id": cat, "pct": round((spent - avg) * 100 / avg),
                    "spent": spent, "avg": round_k(avg)},
            category_id=cat, extra={"suggested_limit": round_k(avg)},
        ))

    # 2. Chegirma kunlari: groceries'ga ko'p mayda xarid
    groceries = [r for r in expenses if r.category_id == "groceries" and local(r) >= this_month]
    if len(groceries) >= DISCOUNT_MIN_TRIPS:
        total = sum(r.amount for r in groceries)
        saving = round_k(total * DISCOUNT_SAVING_RATE)
        if saving > 0:
            weeks = max(1, (today - this_month).days // 7 + 1)
            drafts.append(Draft(
                kind=InsightKind.DISCOUNT_DAYS, action=InsightAction.REMIND_ME,
                icon="shopping-cart", saving=saving, key=f"discount_days:groceries:{period}",
                params={"count": len(groceries), "saving": saving}, category_id="groceries",
                extra={"weekly_amount": round_k(total / weeks)},
            ))

    # 3. Takroriy obunalar (subs): oxirgi 60 kunda har xil nomdagi to'lovlar
    subs_since = today - timedelta(days=60)
    subs: dict[str, list[int]] = defaultdict(list)
    names: dict[str, str] = {}
    for r in expenses:
        if r.category_id == "subs" and local(r) >= subs_since:
            key = _normalize(r.title) or f"#{r.amount}"
            subs[key].append(r.amount)
            names.setdefault(key, r.title or "")
    if len(subs) >= 2:
        monthly = {k: max(v) for k, v in subs.items()}
        cheapest = min(monthly.values())
        shown = [names[k] for k in sorted(monthly, key=lambda k: -monthly[k]) if names[k]][:3]
        drafts.append(Draft(
            kind=InsightKind.SUBSCRIPTIONS, action=InsightAction.REVIEW, icon="repeat",
            saving=cheapest, key=f"subscriptions:subs:{period}",
            params={"count": len(subs), "names": ", ".join(shown) or "—", "saving": cheapest},
            category_id="subs",
        ))

    # 4. Kirim bor, goal'ga auto-save yo'q
    income_30 = sum(r.amount for r in rows if r.type is TransactionType.INCOME
                    and local(r) >= today - timedelta(days=30))
    goals = await uow.goals.list_for_user(user_id)
    if income_30 > 0 and goals and not any(g.auto_save_monthly for g in goals):
        saving = round_k(income_30 * AUTOSAVE_RATE)
        if saving > 0:
            drafts.append(Draft(
                kind=InsightKind.AUTOSAVE, action=InsightAction.TURN_ON_AUTOSAVE,
                icon="piggy-bank", saving=saving, key=f"autosave:{period}",
                params={"saving": saving}, extra={"goal_id": str(goals[0].id)},
            ))
    return drafts


def to_insight(d: Draft, user_id: UUID, now: datetime) -> Insight:
    return Insight(id=uuid7(), user_id=user_id, kind=d.kind, action=d.action, icon=d.icon,
                   saving=d.saving, params=d.params, dedupe_key=d.key, created_at=now,
                   updated_at=now, category_id=d.category_id, extra=d.extra)
