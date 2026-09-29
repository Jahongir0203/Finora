from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.insights.entities import Insight, InsightAction, InsightKind, InsightStatus
from app.infrastructure.db.models import InsightModel

M = InsightModel


def _insight(m: InsightModel) -> Insight:
    return Insight(id=m.id, user_id=m.user_id, kind=InsightKind(m.kind),
                   action=InsightAction(m.action), icon=m.icon, saving=m.saving,
                   params=dict(m.params or {}), dedupe_key=m.dedupe_key,
                   created_at=m.created_at, updated_at=m.updated_at, category_id=m.category_id,
                   status=InsightStatus(m.status), extra=dict(m.extra or {}))


class SqlInsightRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def upsert(self, i: Insight) -> None:
        m = await self._s.scalar(
            select(M).where(M.user_id == i.user_id, M.dedupe_key == i.dedupe_key)
        )
        if m is None:
            self._s.add(M(id=i.id, user_id=i.user_id, kind=i.kind.value, action=i.action.value,
                          icon=i.icon, category_id=i.category_id, saving=i.saving,
                          params=i.params, extra=i.extra, status=i.status.value,
                          dedupe_key=i.dedupe_key, created_at=i.created_at,
                          updated_at=i.updated_at))
        else:
            m.saving, m.params, m.extra, m.updated_at = i.saving, i.params, i.extra, i.updated_at
        await self._s.flush()

    async def list_for_user(self, user_id: UUID, *, include_dismissed: bool) -> list[Insight]:
        stmt = select(M).where(M.user_id == user_id)
        if not include_dismissed:
            stmt = stmt.where(M.status == InsightStatus.ACTIVE.value)
        rows = await self._s.scalars(stmt.order_by(M.saving.desc(), M.id))
        return [_insight(m) for m in rows]

    async def get_for_user(self, user_id: UUID, insight_id: UUID) -> Insight | None:
        m = await self._s.scalar(select(M).where(M.id == insight_id, M.user_id == user_id))
        return _insight(m) if m else None

    async def update(self, i: Insight) -> None:
        await self._s.execute(
            update(M).where(M.id == i.id, M.user_id == i.user_id)
            .values(status=i.status.value, updated_at=i.updated_at)
        )

    async def expire_other(self, user_id: UUID, keep_keys: set[str]) -> None:
        stmt = delete(M).where(M.user_id == user_id, M.status == InsightStatus.ACTIVE.value)
        if keep_keys:
            stmt = stmt.where(M.dedupe_key.not_in(keep_keys))
        await self._s.execute(stmt)
