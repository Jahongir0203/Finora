"""To'lov eslatmalari (BE-1201..1203) va ularning scheduler vazifalari (BE-403 payment_due)."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, time, tzinfo
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import Clock, Notifier
from app.application.common.uow import UnitOfWork
from app.application.finance.accounts import usable_account
from app.application.finance.catalog import CategoryCatalog
from app.application.finance.ledger import Ledger
from app.core.config import Settings
from app.core.i18n import format_amount, t
from app.domain.common.errors import NotFoundError
from app.domain.common.ids import uuid7
from app.domain.common.time import tz_or_default
from app.domain.notifications.entities import NotificationType
from app.domain.reminders.entities import Reminder, Repeat
from app.domain.transactions.entities import Transaction, TransactionType

logger = logging.getLogger("finora.reminders")

PAYMENT_DUE_LOCAL_TIME = time(10, 0)


def reminder_to_dict(r: Reminder, today: date) -> dict[str, Any]:
    return {
        "id": str(r.id), "title": r.title, "category_id": r.category_id, "amount": r.amount,
        "next_due_date": r.next_due_date.isoformat(), "repeat": r.repeat.value,
        "enabled": r.enabled, "due_in_days": r.due_in_days(today),
        "created_at": r.created_at.isoformat(),
    }


@dataclass(frozen=True, slots=True)
class CreateReminderCommand:
    title: str
    category_id: str
    amount: int
    due_date: date
    repeat: Repeat


class ReminderService:
    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings,
                 ledger: Ledger) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings
        self._ledger = ledger

    def today(self, tz: tzinfo) -> date:
        return self._clock.now().astimezone(tz).date()

    async def create(self, ctx: AuthContext, cmd: CreateReminderCommand,
                     idempotency_key: str | None, tz: tzinfo) -> dict[str, Any]:
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                (await CategoryCatalog.load(uow, ctx.user_id)).require(
                    cmd.category_id, TransactionType.EXPENSE)
                now = self._clock.now()
                reminder = Reminder(id=uuid7(), user_id=ctx.user_id, title=cmd.title,
                                    category_id=cmd.category_id, amount=cmd.amount,
                                    next_due_date=cmd.due_date, repeat=cmd.repeat,
                                    created_at=now)
                await uow.reminders.add(reminder)
                return reminder_to_dict(reminder, self.today(tz))

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="reminder.create",
                payload={"title": cmd.title, "category_id": cmd.category_id,
                         "amount": cmd.amount, "due_date": cmd.due_date.isoformat(),
                         "repeat": cmd.repeat.value},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )

    async def list(self, ctx: AuthContext, tz: tzinfo) -> list[Reminder]:
        today = self.today(tz)
        async with self._uow as uow:
            reminders = await uow.reminders.list_for_user(ctx.user_id)
            # Scheduler hali ishlamagan bo'lsa ham o'tgan sanalar ko'rsatilmasin
            changed = [r for r in reminders if r.advance(today)]
            for r in changed:
                r.updated_at = self._clock.now()
                await uow.reminders.update(r)
            if changed:
                await uow.commit()
        return sorted(reminders, key=lambda r: (r.next_due_date, r.id))

    async def get(self, ctx: AuthContext, reminder_id: UUID) -> Reminder:
        async with self._uow as uow:
            reminder = await uow.reminders.get_for_user(ctx.user_id, reminder_id)
        if reminder is None:
            raise NotFoundError()
        return reminder

    async def update(self, ctx: AuthContext, reminder_id: UUID,
                     fields: dict[str, Any]) -> Reminder:
        async with self._uow as uow:
            reminder = await uow.reminders.get_for_user(ctx.user_id, reminder_id)
            if reminder is None:
                raise NotFoundError()
            if "category_id" in fields:
                (await CategoryCatalog.load(uow, ctx.user_id)).require(
                    fields["category_id"], TransactionType.EXPENSE)
            if "due_date" in fields:
                reminder.next_due_date = fields.pop("due_date")
                reminder.anchor_day = reminder.next_due_date.day
            for key in ("title", "category_id", "amount", "repeat", "enabled"):
                if key in fields:
                    setattr(reminder, key, fields[key])
            reminder.updated_at = self._clock.now()
            reminder.__post_init__()
            await uow.reminders.update(reminder)
            await uow.commit()
            return reminder

    async def delete(self, ctx: AuthContext, reminder_id: UUID) -> None:
        async with self._uow as uow:
            if not await uow.reminders.soft_delete(ctx.user_id, reminder_id, self._clock.now()):
                raise NotFoundError()
            await uow.commit()

    async def pay(self, ctx: AuthContext, reminder_id: UUID, account_id: UUID | None,
                  idempotency_key: str | None, tz: tzinfo) -> dict[str, Any]:
        """BE-1203: shu summa va kategoriyada chiqim yaratadi, keyingi sanaga suradi."""
        from app.application.transactions.use_cases import transaction_to_dict

        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                reminder = await uow.reminders.get_for_user(ctx.user_id, reminder_id)
                if reminder is None:
                    raise NotFoundError()
                now = self._clock.now()
                catalog = await CategoryCatalog.load(uow, ctx.user_id)
                catalog.require(reminder.category_id, TransactionType.EXPENSE)
                account = await usable_account(uow, ctx.user_id, account_id, now)
                tx = Transaction(id=uuid7(), user_id=ctx.user_id, account_id=account.id,
                                 type=TransactionType.EXPENSE, amount=reminder.amount,
                                 category_id=reminder.category_id, occurred_at=now,
                                 created_at=now, updated_at=now, title=reminder.title)
                await uow.transactions.add(tx)
                reminder.mark_paid()
                reminder.updated_at = now
                await uow.reminders.update(reminder)
                return {"transaction": transaction_to_dict(tx),
                        "reminder": reminder_to_dict(reminder, self.today(tz))}

            result = await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="reminder.pay",
                payload={"reminder_id": str(reminder_id),
                         "account_id": str(account_id) if account_id else None},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )
        await self._ledger.invalidate(ctx.user_id)
        return result


class ReminderJob:
    """Scheduler (har soat): o'tgan sanalarni suradi (BE-1202) va payment_due yuboradi —
    sanadan 1 kun oldin va shu kuni, foydalanuvchi vaqtida 10:00 dan keyin (BE-403)."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork], clock: Clock,
                 notifier: Notifier) -> None:
        self._uow = uow_factory
        self._clock = clock
        self._notifier = notifier

    async def run(self) -> dict[str, int]:
        now = self._clock.now()
        utc_today = now.date()
        advanced = sent = 0
        tz_cache: dict[UUID, tuple[tzinfo, str]] = {}

        async def user_tz(uow: UnitOfWork, user_id: UUID) -> tuple[tzinfo, str]:
            if user_id not in tz_cache:
                user = await uow.users.get(user_id)
                tz_cache[user_id] = (tz_or_default(user.timezone if user else None),
                                     user.language if user else "uz-Latn")
            return tz_cache[user_id]

        async with self._uow() as uow:
            # UTC+14 gacha bo'lgan zonalar uchun: ertangi UTC sanadan oldingilar nomzod
            for r in await uow.reminders.overdue(date.fromordinal(utc_today.toordinal() + 1)):
                tz, _ = await user_tz(uow, r.user_id)
                if r.advance(now.astimezone(tz).date()):
                    r.updated_at = now
                    await uow.reminders.update(r)
                    advanced += 1
            await uow.commit()
            candidates = await uow.reminders.due_between(
                date.fromordinal(utc_today.toordinal() - 1),
                date.fromordinal(utc_today.toordinal() + 2))
            for r in candidates:
                await user_tz(uow, r.user_id)

        for r in candidates:
            tz, _ = tz_cache[r.user_id]
            local = now.astimezone(tz)
            if local.time() < PAYMENT_DUE_LOCAL_TIME:
                continue
            days = (r.next_due_date - local.date()).days
            if days not in (0, 1):
                continue
            tag = "d0" if days == 0 else "d1"
            when_key = "notif.when.today" if days == 0 else "notif.when.tomorrow"
            title, amount, due = r.title, r.amount, r.next_due_date

            def render(loc: str, title: str = title, amount: int = amount, due: date = due,
                       when_key: str = when_key) -> tuple[str, str]:
                return (t("notif.payment_due.title", loc, title=title, when=t(when_key, loc)),
                        t("notif.payment_due.body", loc, amount=format_amount(amount),
                          date=due.isoformat()))

            if await self._notifier.notify(
                r.user_id, NotificationType.PAYMENT_DUE, render,
                dedupe_key=f"payment_due:{r.id}:{due.isoformat()}:{tag}",
            ):
                sent += 1
        return {"advanced": advanced, "payment_due_sent": sent}


