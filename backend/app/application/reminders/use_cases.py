"""Eslatmalar. Egalik repository'da majburiy, begona eslatma — 404."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import Clock
from app.application.common.uow import UnitOfWork
from app.core.config import Settings
from app.domain.common.errors import NotFoundError
from app.domain.common.ids import uuid7
from app.domain.common.values import ensure_amount, ensure_name
from app.domain.reminders.entities import Reminder, Repeat

_UNSET: Any = object()


def reminder_to_dict(r: Reminder) -> dict[str, Any]:
    return {
        "id": str(r.id),
        "title": r.title,
        "amount": r.amount,
        "due_at": r.due_at.isoformat(),
        "repeat": r.repeat.value,
        "created_at": r.created_at.isoformat(),
    }


@dataclass(frozen=True, slots=True)
class CreateReminderCommand:
    title: str
    due_at: datetime
    repeat: Repeat
    amount: int | None = None


class ReminderService:
    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings

    async def create(self, ctx: AuthContext, cmd: CreateReminderCommand,
                     idempotency_key: str | None) -> dict[str, Any]:
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                reminder = Reminder(id=uuid7(), user_id=ctx.user_id, title=cmd.title,
                                    due_at=cmd.due_at, repeat=cmd.repeat, amount=cmd.amount,
                                    created_at=self._clock.now())
                await uow.reminders.add(reminder)
                return reminder_to_dict(reminder)

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="reminder.create",
                payload={"title": cmd.title, "due_at": cmd.due_at.isoformat(),
                         "repeat": cmd.repeat.value, "amount": cmd.amount},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )

    async def list(self, ctx: AuthContext) -> list[Reminder]:
        async with self._uow as uow:
            return await uow.reminders.list_for_user(ctx.user_id)

    async def get(self, ctx: AuthContext, reminder_id: UUID) -> Reminder:
        async with self._uow as uow:
            reminder = await uow.reminders.get_for_user(ctx.user_id, reminder_id)
        if reminder is None:
            raise NotFoundError()
        return reminder

    async def update(self, ctx: AuthContext, reminder_id: UUID, *, title: str | None = None,
                     due_at: datetime | None = None, repeat: Repeat | None = None,
                     amount: int | None = _UNSET) -> Reminder:
        """amount=None — summani olib tashlash; berilmasa — o'zgarmaydi."""
        async with self._uow as uow:
            reminder = await uow.reminders.get_for_user(ctx.user_id, reminder_id)
            if reminder is None:
                raise NotFoundError()
            if title is not None:
                reminder.title = ensure_name(title)
            if due_at is not None:
                reminder.due_at = due_at
            if repeat is not None:
                reminder.repeat = repeat
            if amount is not _UNSET:
                reminder.amount = None if amount is None else ensure_amount(amount)
            await uow.reminders.update(reminder)
            await uow.commit()
            return reminder

    async def delete(self, ctx: AuthContext, reminder_id: UUID) -> None:
        async with self._uow as uow:
            if not await uow.reminders.delete_for_user(ctx.user_id, reminder_id):
                raise NotFoundError()
            await uow.commit()
