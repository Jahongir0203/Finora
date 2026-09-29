from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.reminders.entities import Reminder, Repeat
from app.infrastructure.db.models import ReminderModel

R = ReminderModel


def _reminder(m: ReminderModel) -> Reminder:
    return Reminder(id=m.id, user_id=m.user_id, title=m.title, category_id=m.category_id,
                    amount=m.amount, next_due_date=m.next_due_date, repeat=Repeat(m.repeat),
                    created_at=m.created_at, updated_at=m.updated_at, enabled=m.enabled,
                    anchor_day=m.anchor_day, deleted_at=m.deleted_at)


class SqlReminderRepository:
    """Har bir so'rov `WHERE id = :id AND user_id = :sub`."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, r: Reminder) -> None:
        assert r.anchor_day is not None and r.updated_at is not None
        self._s.add(R(id=r.id, user_id=r.user_id, title=r.title, category_id=r.category_id,
                      amount=r.amount, next_due_date=r.next_due_date, anchor_day=r.anchor_day,
                      repeat=r.repeat.value, enabled=r.enabled, created_at=r.created_at,
                      updated_at=r.updated_at))
        await self._s.flush()

    async def get_for_user(self, user_id: UUID, reminder_id: UUID) -> Reminder | None:
        m = await self._s.scalar(
            select(R).where(R.id == reminder_id, R.user_id == user_id, R.deleted_at.is_(None))
        )
        return _reminder(m) if m else None

    async def list_for_user(self, user_id: UUID) -> list[Reminder]:
        rows = await self._s.scalars(
            select(R).where(R.user_id == user_id, R.deleted_at.is_(None))
            .order_by(R.next_due_date, R.id)
        )
        return [_reminder(m) for m in rows]

    async def update(self, r: Reminder) -> None:
        await self._s.execute(
            update(R).where(R.id == r.id, R.user_id == r.user_id)
            .values(title=r.title, category_id=r.category_id, amount=r.amount,
                    next_due_date=r.next_due_date, anchor_day=r.anchor_day,
                    repeat=r.repeat.value, enabled=r.enabled, updated_at=r.updated_at)
        )

    async def soft_delete(self, user_id: UUID, reminder_id: UUID, at: datetime) -> bool:
        result = await self._s.execute(
            update(R).where(R.id == reminder_id, R.user_id == user_id, R.deleted_at.is_(None))
            .values(deleted_at=at, updated_at=at)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def due_between(self, start: date, end: date) -> list[Reminder]:
        rows = await self._s.scalars(
            select(R).where(R.enabled.is_(True), R.deleted_at.is_(None),
                            R.next_due_date >= start, R.next_due_date <= end)
            .order_by(R.id)
        )
        return [_reminder(m) for m in rows]

    async def overdue(self, before: date) -> list[Reminder]:
        rows = await self._s.scalars(
            select(R).where(R.enabled.is_(True), R.deleted_at.is_(None),
                            R.next_due_date < before).order_by(R.id)
        )
        return [_reminder(m) for m in rows]

    async def changed_since(self, user_id: UUID, since: datetime,
                            limit: int) -> list[Reminder]:
        rows = await self._s.scalars(
            select(R).where(R.user_id == user_id, R.updated_at > since)
            .order_by(R.updated_at).limit(limit)
        )
        return [_reminder(m) for m in rows]
