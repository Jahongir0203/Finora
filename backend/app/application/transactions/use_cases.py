from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import Clock
from app.application.common.uow import UnitOfWork
from app.core.config import Settings
from app.domain.common.errors import NotFoundError
from app.domain.common.ids import uuid7
from app.domain.transactions.entities import Transaction, TransactionKind


@dataclass(frozen=True, slots=True)
class CreateTransactionCommand:
    kind: TransactionKind
    amount: int
    category: str
    occurred_at: datetime
    note: str | None = None


def transaction_to_dict(tx: Transaction) -> dict[str, Any]:
    return {
        "id": str(tx.id),
        "kind": tx.kind.value,
        "amount": tx.amount,
        "category": tx.category,
        "note": tx.note,
        "occurred_at": tx.occurred_at.isoformat(),
        "created_at": tx.created_at.isoformat(),
    }


class TransactionService:
    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings

    async def create(self, ctx: AuthContext, cmd: CreateTransactionCommand,
                     idempotency_key: str | None) -> dict[str, Any]:
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                tx = Transaction(
                    id=uuid7(), user_id=ctx.user_id, kind=cmd.kind, amount=cmd.amount,
                    category=cmd.category, note=cmd.note, occurred_at=cmd.occurred_at,
                    created_at=self._clock.now(),
                )
                await uow.transactions.add(tx)
                return transaction_to_dict(tx)

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="transaction.create",
                payload={
                    "kind": cmd.kind.value, "amount": cmd.amount, "category": cmd.category,
                    "note": cmd.note, "occurred_at": cmd.occurred_at.isoformat(),
                },
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )

    async def get(self, ctx: AuthContext, tx_id: UUID) -> Transaction:
        async with self._uow as uow:
            tx = await uow.transactions.get_for_user(ctx.user_id, tx_id)
        if tx is None:
            raise NotFoundError()
        return tx

    async def list(self, ctx: AuthContext, *, since: datetime | None, until: datetime | None,
                   limit: int, before_id: UUID | None) -> list[Transaction]:
        async with self._uow as uow:
            return await uow.transactions.list_for_user(
                ctx.user_id, since=since, until=until, limit=limit, before_id=before_id
            )

    async def delete(self, ctx: AuthContext, tx_id: UUID) -> None:
        async with self._uow as uow:
            if not await uow.transactions.delete_for_user(ctx.user_id, tx_id):
                raise NotFoundError()
            await uow.commit()
