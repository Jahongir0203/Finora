from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, case, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.transactions.entities import (
    Transaction,
    TransactionSource,
    TransactionType,
    TransferDirection,
)
from app.domain.transactions.repository import TransactionFilter
from app.infrastructure.db.models import GoalEntryModel, TransactionModel

T = TransactionModel


def _tx(m: TransactionModel) -> Transaction:
    return Transaction(
        id=m.id, user_id=m.user_id, account_id=m.account_id, type=TransactionType(m.type),
        amount=m.amount, category_id=m.category_id, occurred_at=m.occurred_at,
        created_at=m.created_at, updated_at=m.updated_at, title=m.title, note=m.note,
        source=TransactionSource(m.source), receipt_id=m.receipt_id, currency=m.currency,
        client_created_at=m.client_created_at, transfer_peer_id=m.transfer_peer_id,
        direction=TransferDirection(m.direction) if m.direction else None,
        deleted_at=m.deleted_at,
    )


def _values(tx: Transaction) -> dict[str, Any]:
    return {
        "account_id": tx.account_id, "type": tx.type.value, "amount": tx.amount,
        "currency": tx.currency, "category_id": tx.category_id, "title": tx.title,
        "note": tx.note, "source": tx.source.value, "receipt_id": tx.receipt_id,
        "occurred_at": tx.occurred_at, "updated_at": tx.updated_at,
        "deleted_at": tx.deleted_at, "client_created_at": tx.client_created_at,
        "transfer_peer_id": tx.transfer_peer_id,
        "direction": tx.direction.value if tx.direction else None,
    }


def _like(q: str) -> str:
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


class SqlTransactionRepository:
    """Har bir so'rov user_id bilan. `q` qidiruvi Postgres'da pg_trgm GIN indeksidan foydalanadi."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_for_user(self, user_id: UUID, tx_id: UUID) -> Transaction | None:
        m = await self._s.scalar(
            select(T).where(T.id == tx_id, T.user_id == user_id, T.deleted_at.is_(None))
        )
        return _tx(m) if m else None

    async def list_for_user(self, user_id: UUID, flt: TransactionFilter, *, limit: int,
                            after: tuple[datetime, UUID] | None = None,
                            category_ids_by_name: list[str] | None = None) -> list[Transaction]:
        stmt = select(T).where(T.user_id == user_id, T.deleted_at.is_(None))
        if flt.types:
            stmt = stmt.where(T.type.in_([t.value for t in flt.types]))
        if flt.category_id is not None:
            stmt = stmt.where(T.category_id == flt.category_id)
        if flt.account_id is not None:
            stmt = stmt.where(T.account_id == flt.account_id)
        if flt.since is not None:
            stmt = stmt.where(T.occurred_at >= flt.since)
        if flt.until is not None:
            stmt = stmt.where(T.occurred_at < flt.until)
        if flt.q:
            pattern = _like(flt.q)
            conds = [T.title.ilike(pattern, escape="\\"), T.note.ilike(pattern, escape="\\")]
            if category_ids_by_name:
                conds.append(T.category_id.in_(category_ids_by_name))
            stmt = stmt.where(or_(*conds))
        if after is not None:
            at, last_id = after
            stmt = stmt.where(or_(T.occurred_at < at, and_(T.occurred_at == at, T.id < last_id)))
        stmt = stmt.order_by(T.occurred_at.desc(), T.id.desc()).limit(limit)
        return [_tx(m) for m in await self._s.scalars(stmt)]

    async def add(self, tx: Transaction) -> None:
        self._s.add(T(id=tx.id, user_id=tx.user_id, created_at=tx.created_at, **_values(tx)))
        await self._s.flush()

    async def update(self, tx: Transaction) -> None:
        await self._s.execute(
            update(T).where(T.id == tx.id, T.user_id == tx.user_id).values(**_values(tx))
        )

    async def soft_delete(self, user_id: UUID, tx_ids: list[UUID], at: datetime) -> int:
        result = await self._s.execute(
            update(T).where(T.user_id == user_id, T.id.in_(tx_ids), T.deleted_at.is_(None))
            .values(deleted_at=at, updated_at=at)
        )
        return result.rowcount or 0  # type: ignore[attr-defined]

    async def reassign_category(self, user_id: UUID, old: str, new: str, at: datetime) -> int:
        result = await self._s.execute(
            update(T).where(T.user_id == user_id, T.category_id == old)
            .values(category_id=new, updated_at=at)
        )
        return result.rowcount or 0  # type: ignore[attr-defined]

    async def count_for_category(self, user_id: UUID, category_id: str) -> int:
        n = await self._s.scalar(
            select(func.count()).select_from(T).where(
                T.user_id == user_id, T.category_id == category_id, T.deleted_at.is_(None))
        )
        return int(n or 0)

    async def counts_by_category(self, user_id: UUID) -> dict[str, int]:
        rows = await self._s.execute(
            select(T.category_id, func.count()).where(T.user_id == user_id,
                                                      T.deleted_at.is_(None))
            .group_by(T.category_id)
        )
        return {cat: int(n) for cat, n in rows.all()}

    async def has_any(self, user_id: UUID) -> bool:
        return await self._s.scalar(
            select(T.id).where(T.user_id == user_id, T.deleted_at.is_(None),
                               T.type != TransactionType.TRANSFER.value).limit(1)
        ) is not None

    async def changed_since(self, user_id: UUID, since: datetime,
                            limit: int) -> list[Transaction]:
        rows = await self._s.scalars(
            select(T).where(T.user_id == user_id, T.updated_at > since)
            .order_by(T.updated_at, T.id).limit(limit)
        )
        return [_tx(m) for m in rows]


class SqlLedgerQueries:
    """Agregatlar SQL'da (BE-505). Natija keshlanadi (application/finance)."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def balance_deltas(self, user_id: UUID) -> dict[UUID, int]:
        signed = case(
            (T.type == TransactionType.INCOME.value, T.amount),
            (T.direction == TransferDirection.IN.value, T.amount),
            else_=-T.amount,
        )
        rows = await self._s.execute(
            select(T.account_id, func.sum(signed))
            .where(T.user_id == user_id, T.deleted_at.is_(None)).group_by(T.account_id)
        )
        deltas: dict[UUID, int] = {acc: int(total or 0) for acc, total in rows.all()}
        # Goal'ga deposit hisobdan chiqadi, withdraw qaytadi (o'chirilgan goal yozuvlari ham —
        # ular yopilish (close) yozuvi bilan nolga keltirilgan)
        goal_signed = case((GoalEntryModel.kind == "deposit", -GoalEntryModel.amount),
                           else_=GoalEntryModel.amount)
        rows = await self._s.execute(
            select(GoalEntryModel.account_id, func.sum(goal_signed))
            .where(GoalEntryModel.user_id == user_id, GoalEntryModel.account_id.is_not(None))
            .group_by(GoalEntryModel.account_id)
        )
        for acc, total in rows.all():
            deltas[acc] = deltas.get(acc, 0) + int(total or 0)
        return deltas

    async def totals(self, user_id: UUID, since: datetime, until: datetime) -> tuple[int, int]:
        rows = await self._s.execute(
            select(T.type, func.sum(T.amount))
            .where(T.user_id == user_id, T.deleted_at.is_(None),
                   T.type != TransactionType.TRANSFER.value,
                   T.occurred_at >= since, T.occurred_at < until)
            .group_by(T.type)
        )
        by_type = {t: int(total or 0) for t, total in rows.all()}
        return by_type.get("income", 0), by_type.get("expense", 0)

    async def spend_by_category(self, user_id: UUID, since: datetime,
                                until: datetime) -> dict[str, int]:
        rows = await self._s.execute(
            select(T.category_id, func.sum(T.amount))
            .where(T.user_id == user_id, T.deleted_at.is_(None),
                   T.type == TransactionType.EXPENSE.value,
                   T.occurred_at >= since, T.occurred_at < until)
            .group_by(T.category_id)
        )
        return {cat: int(total) for cat, total in rows.all()}

    async def first_transaction_at(self, user_id: UUID) -> datetime | None:
        return await self._s.scalar(
            select(func.min(T.occurred_at)).where(
                T.user_id == user_id, T.deleted_at.is_(None),
                T.type != TransactionType.TRANSFER.value)
        )


