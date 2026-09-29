"""Home agregat endpointi (BE-301): bitta so'rovda butun ekran.

Og'ir qismlar (balans, oylik kirim/chiqim, kategoriya xarajati) Ledger keshi orqali.
Yangi foydalanuvchida summalar 0, ro'yxatlar bo'sh, ai_teaser/budget_summary — null.
"""

from datetime import datetime, timedelta, tzinfo
from typing import Any
from uuid import UUID

from app.application.common.uow import UnitOfWork
from app.application.finance.catalog import CategoryCatalog
from app.application.finance.display import display_currency
from app.application.finance.ledger import Ledger
from app.application.insights.use_cases import InsightService
from app.application.transactions.use_cases import transaction_to_dict
from app.domain.categories.entities import CategoryType
from app.domain.common.errors import NotFoundError
from app.domain.common.time import month_key, parse_tz
from app.domain.transactions.repository import TransactionFilter

UPCOMING_DAYS = 14
RECENT_COUNT = 4


class HomeService:
    def __init__(self, uow: UnitOfWork, ledger: Ledger, insights: InsightService) -> None:
        self._uow = uow
        self._ledger = ledger
        self._insights = insights

    async def execute(self, user_id: UUID, now: datetime, tz: tzinfo,
                      tz_header: str | None, locale: str) -> dict[str, Any]:
        today = now.astimezone(tz).date()
        async with self._uow as uow:
            user = await uow.users.get(user_id)
            if user is None:
                raise NotFoundError()
            if tz_header and parse_tz(tz_header) and tz_header != user.timezone:
                user.timezone = tz_header
                await uow.users.update(user)
                await uow.commit()
            display = await display_currency(uow, user.currency)
            total = await self._ledger.total_balance(uow, user_id)
            income, expenses = await self._ledger.month_totals(uow, user_id, now, tz)
            unread = await uow.notifications.unread_count(user_id)
            recent = await uow.transactions.list_for_user(user_id, TransactionFilter(),
                                                          limit=RECENT_COUNT)
            has_tx = await uow.transactions.has_any(user_id)
            goals = await uow.goals.list_for_user(user_id)
            reminders = await uow.reminders.list_for_user(user_id)
            catalog = await CategoryCatalog.load(uow, user_id, locale)
            limits = [c.monthly_limit for c in catalog
                      if c.monthly_limit and c.type is CategoryType.EXPENSE]
            teaser = await self._insights.teaser(uow, user_id, locale) if has_tx else None

        horizon = today + timedelta(days=UPCOMING_DAYS)
        upcoming = sorted((r for r in reminders
                           if r.enabled and today <= r.next_due_date <= horizon),
                          key=lambda r: (r.next_due_date, r.id))
        balance: dict[str, Any] = {"total": total, "currency": "UZS",
                                   "need_balance": not user.balance_set}
        month: dict[str, Any] = {"income": income, "expenses": expenses}
        if display.active:
            balance["total_display"] = display.amount(total)
            balance["display_currency"] = display.currency
            month["income_display"] = display.amount(income)
            month["expenses_display"] = display.amount(expenses)
        return {
            "user": {"first_name": user.first_name, "initials": user.initials},
            "balance": balance,
            "month": month,
            "unread_notifications": unread,
            "get_started": {"balance": user.balance_set, "transaction": has_tx,
                            "goal": bool(goals), "reminder": bool(reminders)},
            "ai_teaser": teaser,
            "budget_summary": ({"month": month_key(today), "spent": expenses,
                                "limit": sum(limits)} if limits else None),
            "upcoming_payments": [
                {"id": str(r.id), "title": r.title, "amount": r.amount,
                 "due_date": r.next_due_date.isoformat(), "category_id": r.category_id}
                for r in upcoming],
            "recent_transactions": [transaction_to_dict(tx, display) for tx in recent],
        }
