from uuid import UUID

from sqlalchemy import case, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.goals.entities import EntryKind, Goal, GoalEntry
from app.infrastructure.db.models import GoalEntryModel, GoalModel


def _goal(m: GoalModel) -> Goal:
    return Goal(id=m.id, user_id=m.user_id, name=m.name, target_amount=m.target_amount,
                created_at=m.created_at)


class SqlGoalRepository:
    """Har bir so'rov `WHERE id = :id AND user_id = :sub` — egalik shu yerda majburiy."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_for_user(self, user_id: UUID, goal_id: UUID, *, lock: bool = False) -> Goal | None:
        stmt = select(GoalModel).where(GoalModel.id == goal_id, GoalModel.user_id == user_id)
        if lock:
            stmt = stmt.with_for_update()
        m = await self._s.scalar(stmt)
        return _goal(m) if m else None

    async def list_for_user(self, user_id: UUID) -> list[Goal]:
        rows = await self._s.scalars(
            select(GoalModel).where(GoalModel.user_id == user_id).order_by(GoalModel.id.desc())
        )
        return [_goal(m) for m in rows]

    async def add(self, goal: Goal) -> None:
        self._s.add(GoalModel(id=goal.id, user_id=goal.user_id, name=goal.name,
                              target_amount=goal.target_amount, created_at=goal.created_at))

    async def update(self, goal: Goal) -> None:
        await self._s.execute(
            update(GoalModel)
            .where(GoalModel.id == goal.id, GoalModel.user_id == goal.user_id)
            .values(name=goal.name, target_amount=goal.target_amount)
        )

    async def delete_for_user(self, user_id: UUID, goal_id: UUID) -> bool:
        await self._s.execute(
            delete(GoalEntryModel).where(GoalEntryModel.goal_id == goal_id,
                                         GoalEntryModel.user_id == user_id)
        )
        result = await self._s.execute(
            delete(GoalModel).where(GoalModel.id == goal_id, GoalModel.user_id == user_id)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def saved_amount(self, user_id: UUID, goal_id: UUID) -> int:
        signed = case(
            (GoalEntryModel.kind == EntryKind.WITHDRAW.value, -GoalEntryModel.amount),
            else_=GoalEntryModel.amount,
        )
        total = await self._s.scalar(
            select(func.coalesce(func.sum(signed), 0)).where(
                GoalEntryModel.goal_id == goal_id, GoalEntryModel.user_id == user_id
            )
        )
        return int(total or 0)

    async def add_entry(self, entry: GoalEntry) -> None:
        self._s.add(GoalEntryModel(id=entry.id, goal_id=entry.goal_id, user_id=entry.user_id,
                                   kind=entry.kind.value, amount=entry.amount,
                                   created_at=entry.created_at))
        await self._s.flush()

    async def list_entries(self, user_id: UUID, goal_id: UUID) -> list[GoalEntry]:
        rows = await self._s.scalars(
            select(GoalEntryModel)
            .where(GoalEntryModel.goal_id == goal_id, GoalEntryModel.user_id == user_id)
            .order_by(GoalEntryModel.id.desc())
        )
        return [GoalEntry(id=m.id, goal_id=m.goal_id, user_id=m.user_id, kind=EntryKind(m.kind),
                          amount=m.amount, created_at=m.created_at) for m in rows]
