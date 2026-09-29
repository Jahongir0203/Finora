"""Statistika (BE-801). Faqat chiqimlar; davr chegaralari foydalanuvchi vaqt zonasida."""

import calendar
from dataclasses import dataclass
from datetime import date, datetime, timedelta, tzinfo
from enum import StrEnum
from typing import Any
from uuid import UUID

from app.application.common.uow import UnitOfWork
from app.application.finance.display import display_currency
from app.domain.common.time import add_months, local_midnight, month_start, week_start
from app.domain.transactions.entities import TransactionType
from app.domain.transactions.repository import TransactionFilter

MIN_DATA_DAYS = 7
SCAN_LIMIT = 100_000
_WEEKDAYS = ("M", "T", "W", "T", "F", "S", "S")


class StatsPeriod(StrEnum):
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


@dataclass(frozen=True, slots=True)
class Bucket:
    label: str
    start: date
    end: date  # kirmaydi


def buckets(period: StatsPeriod, anchor: date) -> list[Bucket]:
    if period is StatsPeriod.WEEK:
        start = week_start(anchor)
        return [Bucket(_WEEKDAYS[i], start + timedelta(days=i), start + timedelta(days=i + 1))
                for i in range(7)]
    if period is StatsPeriod.MONTH:
        start = month_start(anchor)
        end = add_months(start, 1)
        out, i = [], 0
        while start + timedelta(days=7 * i) < end:
            b_start = start + timedelta(days=7 * i)
            out.append(Bucket(f"W{i + 1}", b_start, min(b_start + timedelta(days=7), end)))
            i += 1
        return out
    first = date(anchor.year, 1, 1)
    return [Bucket(calendar.month_abbr[m], add_months(first, m - 1), add_months(first, m))
            for m in range(1, 13)]


def previous_anchor(period: StatsPeriod, anchor: date) -> date:
    if period is StatsPeriod.WEEK:
        return anchor - timedelta(days=7)
    if period is StatsPeriod.MONTH:
        return add_months(month_start(anchor), -1)
    return date(anchor.year - 1, 1, 1)


def percentages(amounts: list[int]) -> list[int]:
    """Eng katta qoldiq usuli: yaxlitlangan foizlar yig'indisi aniq 100."""
    total = sum(amounts)
    if total <= 0:
        return [0] * len(amounts)
    raw = [a * 100 / total for a in amounts]
    floors = [int(r) for r in raw]
    order = sorted(range(len(raw)), key=lambda i: raw[i] - floors[i], reverse=True)
    for i in order[: 100 - sum(floors)]:
        floors[i] += 1
    return floors


async def _expenses(uow: UnitOfWork, user_id: UUID, start: date, end: date,
                    tz: tzinfo) -> list[tuple[date, str, int]]:
    rows = await uow.transactions.list_for_user(
        user_id, TransactionFilter(types=(TransactionType.EXPENSE,),
                                   since=local_midnight(start, tz), until=local_midnight(end, tz)),
        limit=SCAN_LIMIT)
    return [(r.occurred_at.astimezone(tz).date(), r.category_id, r.amount) for r in rows]


class StatsService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: UUID, period: StatsPeriod, anchor: date, tz: tzinfo,
                      now: datetime) -> dict[str, Any]:
        today = now.astimezone(tz).date()
        bs = buckets(period, anchor)
        prev = buckets(period, previous_anchor(period, anchor))
        async with self._uow as uow:
            rows = await _expenses(uow, user_id, bs[0].start, bs[-1].end, tz)
            prev_rows = await _expenses(uow, user_id, prev[0].start, prev[-1].end, tz)
            first = await uow.ledger.first_transaction_at(user_id)
            user = await uow.users.get(user_id)
            display = await display_currency(uow, user.currency if user else "UZS")

        bars = []
        for b in bs:
            value = sum(a for d, _, a in rows if b.start <= d < b.end)
            bars.append({"label": b.label, "value": value,
                         "current": b.start <= today < b.end,
                         "future": b.start > today})
        total = sum(a for _, _, a in rows)
        prev_total = sum(a for _, _, a in prev_rows)
        change = round((total - prev_total) * 100 / prev_total) if prev_total else None

        by_cat: dict[str, int] = {}
        for _, cat, a in rows:
            by_cat[cat] = by_cat.get(cat, 0) + a
        ordered = sorted(by_cat.items(), key=lambda kv: (-kv[1], kv[0]))
        pcts = percentages([a for _, a in ordered])
        out: dict[str, Any] = {
            "period": period.value, "from": bs[0].start.isoformat(),
            "to": (bs[-1].end - timedelta(days=1)).isoformat(),
            "total_spent": total, "previous_total": prev_total, "change_pct": change,
            "bars": bars,
            "breakdown": [{"category_id": c, "amount": a, "pct": p}
                          for (c, a), p in zip(ordered, pcts, strict=True)],
            "has_enough_data": (first is not None
                                and first.astimezone(tz).date() <= today - timedelta(
                                    days=MIN_DATA_DAYS)),
        }
        if display.active:
            out["total_spent_display"] = display.amount(total)
            out["display_currency"] = display.currency
        return out
