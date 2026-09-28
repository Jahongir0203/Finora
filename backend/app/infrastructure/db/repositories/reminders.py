from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.reminders.entities import Reminder, Repeat
from app.infrastructure.db.models import ReminderModel


def _reminder(m: ReminderModel) -> Reminder:
    return Reminder(id=m.id, user_id=m.user_id, title=m.title, amount=m.amount,
                    due_at=m.due_at, repeat=Repeat(m.repeat), created_at=m.created_at)


class SqlReminderRepository:
    """Har bir so'rov `WHERE id = :id AND user_id = :sub`."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, reminder: Reminder) -> None:
        self._s.add(ReminderModel(
            id=reminder.id, user_id=reminder.user_id, title=reminder.title,
            amount=reminder.amount, due_at=reminder.due_at, repeat=reminder.repeat.value,
            created_at=reminder.created_at,
        ))
        await self._s.flush()

    async def get_for_user(self, user_id: UUID, reminder_id: UUID) -> Reminder | None:
        m = await self._s.scalar(
            select(ReminderModel).where(ReminderModel.id == reminder_id,
                                        ReminderModel.user_id == user_id)
        )
        return _reminder(m) if m else None

    async def list_for_user(self, user_id: UUID) -> list[Reminder]:
        rows = await self._s.scalars(
            select(ReminderModel).where(ReminderModel.user_id == user_id)
            .order_by(ReminderModel.due_at)
        )
        return [_reminder(m) for m in rows]

    async def update(self, reminder: Reminder) -> None:
        await self._s.execute(
            update(ReminderModel)
            .where(ReminderModel.id == reminder.id, ReminderModel.user_id == reminder.user_id)
            .values(title=reminder.title, amount=reminder.amount, due_at=reminder.due_at,
                    repeat=reminder.repeat.value)
        )

    async def delete_for_user(self, user_id: UUID, reminder_id: UUID) -> bool:
        result = await self._s.execute(
            delete(ReminderModel).where(ReminderModel.id == reminder_id,
                                        ReminderModel.user_id == user_id)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]
