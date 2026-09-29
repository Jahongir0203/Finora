from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exports.entities import Export, ExportFormat, ExportPeriod, ExportStatus
from app.domain.transactions.entities import TransactionType
from app.infrastructure.db.models import ExportModel

X = ExportModel


def _export(m: ExportModel) -> Export:
    return Export(
        id=m.id, user_id=m.user_id, period=ExportPeriod(m.period), format=ExportFormat(m.format),
        include=[TransactionType(t) for t in m.include], range_start=m.range_start,
        range_end=m.range_end, file_name=m.file_name, created_at=m.created_at,
        expires_at=m.expires_at, status=ExportStatus(m.status), file_key=m.file_key,
        error_code=m.error_code, row_count=m.row_count, ready_at=m.ready_at,
        downloaded_at=m.downloaded_at, language=m.language, timezone=m.timezone,
    )


class SqlExportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, e: Export) -> None:
        self._s.add(X(
            id=e.id, user_id=e.user_id, status=e.status.value, period=e.period.value,
            format=e.format.value, include=[t.value for t in e.include],
            range_start=e.range_start, range_end=e.range_end, file_name=e.file_name,
            language=e.language, timezone=e.timezone, created_at=e.created_at,
            expires_at=e.expires_at, row_count=e.row_count,
        ))
        await self._s.flush()

    async def get_for_user(self, user_id: UUID, export_id: UUID) -> Export | None:
        m = await self._s.scalar(select(X).where(X.id == export_id, X.user_id == user_id))
        return _export(m) if m else None

    async def get(self, export_id: UUID) -> Export | None:
        m = await self._s.get(X, export_id, populate_existing=True)
        return _export(m) if m else None

    async def update(self, e: Export) -> None:
        await self._s.execute(
            update(X).where(X.id == e.id).values(
                status=e.status.value, file_key=e.file_key, error_code=e.error_code,
                row_count=e.row_count, ready_at=e.ready_at, expires_at=e.expires_at,
            )
        )

    async def mark_downloaded(self, export_id: UUID, at: datetime) -> bool:
        result = await self._s.execute(
            update(X).where(X.id == export_id, X.downloaded_at.is_(None))
            .values(downloaded_at=at)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def pending(self, created_before: datetime) -> list[Export]:
        rows = await self._s.scalars(
            select(X).where(X.status == ExportStatus.PENDING.value,
                            X.created_at < created_before).limit(100)
        )
        return [_export(m) for m in rows]

    async def list_expired(self, now: datetime) -> list[Export]:
        rows = await self._s.scalars(
            select(X).where(or_(X.expires_at <= now, X.downloaded_at.is_not(None)))
        )
        return [_export(m) for m in rows]

    async def delete(self, export_id: UUID) -> None:
        await self._s.execute(delete(X).where(X.id == export_id))

    async def file_keys_for_user(self, user_id: UUID) -> list[str]:
        rows = await self._s.scalars(
            select(X.file_key).where(X.user_id == user_id, X.file_key.is_not(None))
        )
        return [k for k in rows if k]
