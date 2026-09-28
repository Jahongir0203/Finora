from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.transactions.entities import Transaction, TransactionKind
from app.infrastructure.db.models import TransactionModel


def _tx(m: TransactionModel) -> Transaction:
    return Transaction(id=m.id, user_id=m.user_id, kind=TransactionKind(m.kind), amount=m.amount,
                       category=m.category, note=m.note, occurred_at=m.occurred_at,
                       created_at=m.created_at)


class SqlTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_for_user(self, user_id: UUID, tx_id: UUID) -> Transaction | None:
        m = await self._s.scalar(
            select(TransactionModel).where(TransactionModel.id == tx_id,
                                           TransactionModel.user_id == user_id)
        )
        return _tx(m) if m else None

    async def list_for_user(self, user_id: UUID, *, since: datetime | None = None,
                            until: datetime | None = None, limit: int = 50,
                            before_id: UUID | None = None) -> list[Transaction]:
        stmt = select(TransactionModel).where(TransactionModel.user_id == user_id)
        if since is not None:
            stmt = stmt.where(TransactionModel.occurred_at >= since)
        if until is not None:
            stmt = stmt.where(TransactionModel.occurred_at < until)
        if before_id is not None:
            stmt = stmt.where(TransactionModel.id < before_id)
        stmt = stmt.order_by(TransactionModel.id.desc()).limit(limit)
        return [_tx(m) for m in await self._s.scalars(stmt)]

    async def add(self, tx: Transaction) -> None:
        self._s.add(TransactionModel(
            id=tx.id, user_id=tx.user_id, kind=tx.kind.value, amount=tx.amount,
            category=tx.category, note=tx.note, occurred_at=tx.occurred_at,
            created_at=tx.created_at,
        ))
        await self._s.flush()

    async def delete_for_user(self, user_id: UUID, tx_id: UUID) -> bool:
        result = await self._s.execute(
            delete(TransactionModel).where(TransactionModel.id == tx_id,
                                           TransactionModel.user_id == user_id)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def totals_by_category(self, user_id: UUID, since: datetime,
                                 until: datetime) -> dict[str, int]:
        rows = await self._s.execute(
            select(TransactionModel.category, func.sum(TransactionModel.amount))
            .where(TransactionModel.user_id == user_id,
                   TransactionModel.kind == TransactionKind.EXPENSE.value,
                   TransactionModel.occurred_at >= since, TransactionModel.occurred_at < until)
            .group_by(TransactionModel.category)
        )
        return {cat: int(total) for cat, total in rows.all()}
