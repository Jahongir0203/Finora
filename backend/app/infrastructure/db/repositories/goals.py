from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, case, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.goals.entities import EntryKind, EntrySource, Goal, GoalEntry
from app.infrastructure.db.models import GoalEntryModel, GoalModel

E = GoalEntryModel


def _goal(m: GoalModel) -> Goal:
    return Goal(id=m.id, user_id=m.user_id, name=m.name, target_amount=m.target_amount,
                created_at=m.created_at, updated_at=m.updated_at or m.created_at, icon=m.icon,
                deadline=m.deadline, auto_save_monthly=m.auto_save_monthly,
                auto_save_day=m.auto_save_day, deleted_at=m.deleted_at)


def _entry(m: GoalEntryModel) -> GoalEntry:
    return GoalEntry(id=m.id, goal_id=m.goal_id, user_id=m.user_id, kind=EntryKind(m.kind),
                     amount=m.amount, created_at=m.created_at, account_id=m.account_id,
                     source=EntrySource(m.source), dedupe_key=m.dedupe_key)


_SIGNED = case((E.kind == EntryKind.WITHDRAW.value, -E.amount), else_=E.amount)


class SqlGoalRepository:
    """Har bir so'rov `WHERE id = :id AND user_id = :sub` — egalik shu yerda majburiy."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_for_user(
        self, user_id: UUID, goal_id: UUID, *, lock: bool = False
    ) -> Goal | None:
        stmt = select(GoalModel).where(GoalModel.id == goal_id, GoalModel.user_id == user_id,
                                       GoalModel.deleted_at.is_(None))
        if lock:
            stmt = stmt.with_for_update()
        m = await self._s.scalar(stmt)
        return _goal(m) if m else None

    async def list_for_user(self, user_id: UUID) -> list[Goal]:
        rows = await self._s.scalars(
            select(GoalModel).where(GoalModel.user_id == user_id, GoalModel.deleted_at.is_(None))
            .order_by(GoalModel.id.desc())
        )
        return [_goal(m) for m in rows]

    async def add(self, goal: Goal) -> None:
        self._s.add(GoalModel(
            id=goal.id, user_id=goal.user_id, name=goal.name, target_amount=goal.target_amount,
            created_at=goal.created_at, updated_at=goal.updated_at, icon=goal.icon,
            deadline=goal.deadline, auto_save_monthly=goal.auto_save_monthly,
            auto_save_day=goal.auto_save_day,
        ))
        await self._s.flush()

    async def update(self, goal: Goal) -> None:
        await self._s.execute(
            update(GoalModel)
            .where(GoalModel.id == goal.id, GoalModel.user_id == goal.user_id)
            .values(name=goal.name, target_amount=goal.target_amount, icon=goal.icon,
                    deadline=goal.deadline, auto_save_monthly=goal.auto_save_monthly,
                    auto_save_day=goal.auto_save_day, updated_at=goal.updated_at)
        )

    async def soft_delete(self, user_id: UUID, goal_id: UUID, at: datetime) -> bool:
        result = await self._s.execute(
            update(GoalModel)
            .where(GoalModel.id == goal_id, GoalModel.user_id == user_id,
                   GoalModel.deleted_at.is_(None))
            .values(deleted_at=at, updated_at=at)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def saved_amount(self, user_id: UUID, goal_id: UUID) -> int:
        total = await self._s.scalar(
            select(func.coalesce(func.sum(_SIGNED), 0))
            .where(E.goal_id == goal_id, E.user_id == user_id)
        )
        return int(total or 0)

    async def account_backed_amount(self, user_id: UUID, goal_id: UUID) -> int:
        total = await self._s.scalar(
            select(func.coalesce(func.sum(_SIGNED), 0))
            .where(E.goal_id == goal_id, E.user_id == user_id, E.account_id.is_not(None))
        )
        return int(total or 0)

    async def saved_amounts(self, user_id: UUID) -> dict[UUID, int]:
        rows = await self._s.execute(
            select(E.goal_id, func.sum(_SIGNED)).where(E.user_id == user_id).group_by(E.goal_id)
        )
        return {gid: int(total or 0) for gid, total in rows.all()}

    async def add_entry(self, entry: GoalEntry) -> bool:
        m = E(id=entry.id, goal_id=entry.goal_id, user_id=entry.user_id, kind=entry.kind.value,
              amount=entry.amount, created_at=entry.created_at, account_id=entry.account_id,
              source=entry.source.value, dedupe_key=entry.dedupe_key)
        if entry.dedupe_key is None:
            self._s.add(m)
            await self._s.flush()
            return True
        try:
            async with self._s.begin_nested():
                self._s.add(m)
                await self._s.flush()
        except IntegrityError:
            return False
        return True

    async def list_entries(self, user_id: UUID, goal_id: UUID, *, limit: int,
                           after: tuple[datetime, UUID] | None = None) -> list[GoalEntry]:
        stmt = select(E).where(E.goal_id == goal_id, E.user_id == user_id)
        if after is not None:
            at, last_id = after
            stmt = stmt.where(or_(E.created_at < at, and_(E.created_at == at, E.id < last_id)))
        rows = await self._s.scalars(stmt.order_by(E.created_at.desc(), E.id.desc()).limit(limit))
        return [_entry(m) for m in rows]

    async def with_auto_save(self) -> list[Goal]:
        rows = await self._s.scalars(
            select(GoalModel).where(GoalModel.auto_save_monthly.is_not(None),
                                    GoalModel.deleted_at.is_(None))
            .order_by(GoalModel.id)
        )
        return [_goal(m) for m in rows]

    async def changed_since(self, user_id: UUID, since: datetime, limit: int) -> list[Goal]:
        rows = await self._s.scalars(
            select(GoalModel).where(GoalModel.user_id == user_id, GoalModel.updated_at > since)
            .order_by(GoalModel.updated_at).limit(limit)
        )
        return [_goal(m) for m in rows]
