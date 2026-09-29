from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.receipts.entities import Receipt, ReceiptItem, ReceiptSource
from app.infrastructure.db.models import ReceiptModel

R = ReceiptModel


def _receipt(m: ReceiptModel) -> Receipt:
    items = [ReceiptItem(name=str(i.get("name", "")), quantity=float(i.get("quantity", 1)),
                         price=int(i.get("price", 0))) for i in (m.items or [])]
    return Receipt(id=m.id, user_id=m.user_id, created_at=m.created_at,
                   source=ReceiptSource(m.source), file_key=m.file_key,
                   content_type=m.content_type, size_bytes=m.size_bytes, merchant=m.merchant,
                   total=m.total, occurred_at=m.occurred_at, items=items,
                   suggested_category_id=m.suggested_category_id, confidence=m.confidence,
                   confirmed_at=m.confirmed_at, fiscal_sign=m.fiscal_sign)


class SqlReceiptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, r: Receipt) -> None:
        self._s.add(R(
            id=r.id, user_id=r.user_id, source=r.source.value, file_key=r.file_key,
            content_type=r.content_type, size_bytes=r.size_bytes, merchant=r.merchant,
            total=r.total, occurred_at=r.occurred_at, items=[i.to_dict() for i in r.items],
            suggested_category_id=r.suggested_category_id, confidence=r.confidence,
            fiscal_sign=r.fiscal_sign, created_at=r.created_at, confirmed_at=r.confirmed_at,
        ))
        await self._s.flush()

    async def get_for_user(self, user_id: UUID, receipt_id: UUID) -> Receipt | None:
        m = await self._s.scalar(select(R).where(R.id == receipt_id, R.user_id == user_id))
        return _receipt(m) if m else None

    async def get(self, receipt_id: UUID) -> Receipt | None:
        m = await self._s.get(R, receipt_id)
        return _receipt(m) if m else None

    async def list_for_user(self, user_id: UUID, *, limit: int,
                            after: tuple[datetime, UUID] | None = None) -> list[Receipt]:
        stmt = select(R).where(R.user_id == user_id)
        if after is not None:
            at, last_id = after
            stmt = stmt.where(or_(R.created_at < at, and_(R.created_at == at, R.id < last_id)))
        rows = await self._s.scalars(stmt.order_by(R.created_at.desc(), R.id.desc()).limit(limit))
        return [_receipt(m) for m in rows]

    async def confirm(self, user_id: UUID, receipt_id: UUID, at: datetime) -> bool:
        result = await self._s.execute(
            update(R).where(R.id == receipt_id, R.user_id == user_id).values(confirmed_at=at)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def delete_for_user(self, user_id: UUID, receipt_id: UUID) -> bool:
        result = await self._s.execute(
            delete(R).where(R.id == receipt_id, R.user_id == user_id)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def unconfirmed_before(self, before: datetime) -> list[Receipt]:
        rows = await self._s.scalars(
            select(R).where(R.confirmed_at.is_(None), R.created_at < before).limit(1000)
        )
        return [_receipt(m) for m in rows]

    async def delete(self, receipt_id: UUID) -> None:
        await self._s.execute(delete(R).where(R.id == receipt_id))

    async def file_keys_for_user(self, user_id: UUID) -> list[str]:
        rows = await self._s.scalars(
            select(R.file_key).where(R.user_id == user_id, R.file_key.is_not(None))
        )
        return [k for k in rows if k]
