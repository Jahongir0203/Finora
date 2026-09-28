from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exports.entities import Export
from app.infrastructure.db.models import ExportModel


def _export(m: ExportModel) -> Export:
    return Export(id=m.id, user_id=m.user_id, file_key=m.file_key,
                  download_token_hash=m.download_token_hash, created_at=m.created_at,
                  expires_at=m.expires_at, downloaded_at=m.downloaded_at)


class SqlExportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, export: Export) -> None:
        self._s.add(ExportModel(
            id=export.id, user_id=export.user_id, file_key=export.file_key,
            download_token_hash=export.download_token_hash, created_at=export.created_at,
            expires_at=export.expires_at,
        ))

    async def get_by_token_hash(self, token_hash: str) -> Export | None:
        m = await self._s.scalar(
            select(ExportModel).where(ExportModel.download_token_hash == token_hash)
        )
        return _export(m) if m else None

    async def mark_downloaded(self, export_id: UUID, at: datetime) -> bool:
        result = await self._s.execute(
            update(ExportModel)
            .where(ExportModel.id == export_id, ExportModel.downloaded_at.is_(None))
            .values(downloaded_at=at)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def list_expired(self, now: datetime) -> list[Export]:
        rows = await self._s.scalars(
            select(ExportModel).where(
                or_(ExportModel.expires_at <= now, ExportModel.downloaded_at.is_not(None))
            )
        )
        return [_export(m) for m in rows]

    async def delete(self, export_id: UUID) -> None:
        await self._s.execute(delete(ExportModel).where(ExportModel.id == export_id))

    async def file_keys_for_user(self, user_id: UUID) -> list[str]:
        rows = await self._s.scalars(
            select(ExportModel.file_key).where(ExportModel.user_id == user_id)
        )
        return list(rows)
