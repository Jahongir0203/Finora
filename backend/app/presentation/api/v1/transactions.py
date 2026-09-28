from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.application.transactions.use_cases import (
    CreateTransactionCommand,
    TransactionService,
    transaction_to_dict,
)
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey
from app.presentation.schemas.transactions import TransactionCreateIn, TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _svc(c: ContainerDep) -> TransactionService:
    return TransactionService(c.uow(), c.clock, c.settings)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransactionOut)
async def create_transaction(body: TransactionCreateIn, ctx: AuthDep, c: ContainerDep,
                             idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    cmd = CreateTransactionCommand(kind=body.kind, amount=body.amount, category=body.category,
                                   occurred_at=body.occurred_at, note=body.note)
    return await _svc(c).create(ctx, cmd, idempotency_key)


@router.get("", response_model=list[TransactionOut])
async def list_transactions(
    ctx: AuthDep,
    c: ContainerDep,
    since: datetime | None = None,
    until: datetime | None = None,
    before_id: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[dict[str, Any]]:
    txs = await _svc(c).list(ctx, since=since, until=until, limit=limit, before_id=before_id)
    return [transaction_to_dict(t) for t in txs]


@router.get("/{tx_id}", response_model=TransactionOut)
async def get_transaction(tx_id: UUID, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return transaction_to_dict(await _svc(c).get(ctx, tx_id))


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(tx_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await _svc(c).delete(ctx, tx_id)
