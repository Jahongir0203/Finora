from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.idempotency import IdempotencyConflict, IdempotencyRecord
from app.infrastructure.db.models import IdempotencyKeyModel


class SqlIdempotencyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get(self, user_id: UUID, key: str) -> IdempotencyRecord | None:
        m = await self._s.get(IdempotencyKeyModel, (user_id, key), populate_existing=True)
        if m is None:
            return None
        return IdempotencyRecord(user_id=m.user_id, key=m.key, fingerprint=m.fingerprint,
                                 response=m.response, created_at=m.created_at)

    async def delete_stale(self, user_id: UUID, key: str, before: datetime) -> None:
        await self._s.execute(
            delete(IdempotencyKeyModel).where(
                IdempotencyKeyModel.user_id == user_id, IdempotencyKeyModel.key == key,
                IdempotencyKeyModel.created_at < before,
            )
        )

    async def reserve(self, record: IdempotencyRecord) -> None:
        self._s.add(IdempotencyKeyModel(user_id=record.user_id, key=record.key,
                                        fingerprint=record.fingerprint, response=record.response,
                                        created_at=record.created_at))
        try:
            await self._s.flush()
        except IntegrityError as exc:
            raise IdempotencyConflict() from exc

    async def set_response(self, user_id: UUID, key: str, response: dict[str, Any]) -> None:
        await self._s.execute(
            update(IdempotencyKeyModel)
            .where(IdempotencyKeyModel.user_id == user_id, IdempotencyKeyModel.key == key)
            .values(response=response)
        )

    async def purge_older_than(self, before: datetime) -> int:
        result = await self._s.execute(
            delete(IdempotencyKeyModel).where(IdempotencyKeyModel.created_at < before)
        )
        return result.rowcount or 0  # type: ignore[attr-defined]
