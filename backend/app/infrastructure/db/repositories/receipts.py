from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.receipts.entities import Receipt
from app.infrastructure.db.models import ReceiptModel


def _receipt(m: ReceiptModel) -> Receipt:
    return Receipt(id=m.id, user_id=m.user_id, file_key=m.file_key,
                   content_type=m.content_type, size_bytes=m.size_bytes, created_at=m.created_at)


class SqlReceiptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, receipt: Receipt) -> None:
        self._s.add(ReceiptModel(
            id=receipt.id, user_id=receipt.user_id, file_key=receipt.file_key,
            content_type=receipt.content_type, size_bytes=receipt.size_bytes,
            created_at=receipt.created_at,
        ))
        await self._s.flush()

    async def get_for_user(self, user_id: UUID, receipt_id: UUID) -> Receipt | None:
        m = await self._s.scalar(
            select(ReceiptModel).where(ReceiptModel.id == receipt_id,
                                       ReceiptModel.user_id == user_id)
        )
        return _receipt(m) if m else None

    async def get(self, receipt_id: UUID) -> Receipt | None:
        m = await self._s.get(ReceiptModel, receipt_id)
        return _receipt(m) if m else None

    async def list_for_user(self, user_id: UUID, limit: int = 50) -> list[Receipt]:
        rows = await self._s.scalars(
            select(ReceiptModel).where(ReceiptModel.user_id == user_id)
            .order_by(ReceiptModel.id.desc()).limit(limit)
        )
        return [_receipt(m) for m in rows]

    async def delete_for_user(self, user_id: UUID, receipt_id: UUID) -> bool:
        result = await self._s.execute(
            delete(ReceiptModel).where(ReceiptModel.id == receipt_id,
                                       ReceiptModel.user_id == user_id)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def file_keys_for_user(self, user_id: UUID) -> list[str]:
        rows = await self._s.scalars(
            select(ReceiptModel.file_key).where(ReceiptModel.user_id == user_id)
        )
        return list(rows)
