from datetime import date, timedelta
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.application.transactions.use_cases import (
    CreateTransactionCommand,
    UpdateTransactionCommand,
    transaction_to_dict,
)
from app.domain.common.time import local_midnight
from app.domain.transactions.entities import TransactionType
from app.domain.transactions.repository import TransactionFilter
from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey, TzDep
from app.presentation.schemas.categories import CategoryRef
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.transactions import (
    TransactionCreatedOut,
    TransactionCreateIn,
    TransactionOut,
    TransactionPageOut,
    TransactionUpdateIn,
)

router = APIRouter(prefix="/transactions", tags=["transactions"], responses=ERROR_RESPONSES)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransactionCreatedOut)
async def create_transaction(body: TransactionCreateIn, ctx: AuthDep, c: ContainerDep,
                             tz: TzDep, idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    """Kategoriya turiga mos bo'lishi shart (422 category_type_mismatch). `account_id`
    berilmasa — standart hisob. Javobda yangilangan `balance.total` (BE-502)."""
    cmd = CreateTransactionCommand(
        type=body.type, amount=body.amount, category_id=body.category_id, title=body.title,
        note=body.note, account_id=body.account_id, occurred_at=body.occurred_at,
        receipt_id=body.receipt_id, client_created_at=body.client_created_at)
    return await factories.transactions(c).create(ctx, cmd, idempotency_key, tz)


@router.get("", response_model=TransactionPageOut)
async def list_transactions(
    ctx: AuthDep,
    c: ContainerDep,
    tz: TzDep,
    q: Annotated[str | None, Query(min_length=1, max_length=64)] = None,
    type: TransactionType | None = None,
    category_id: CategoryRef | None = None,
    account_id: UUID | None = None,
    from_: Annotated[date | None, Query(alias="from")] = None,
    to: date | None = None,
    cursor: Annotated[str | None, Query(max_length=200)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
) -> dict[str, Any]:
    """Activity: qidiruv (title, note, kategoriya nomi), filtrlar, kunlik `groups` (BE-503)."""
    flt = TransactionFilter(
        q=q.strip() if q else None, types=(type,) if type else (), category_id=category_id,
        account_id=account_id,
        since=local_midnight(from_, tz) if from_ else None,
        until=local_midnight(to + timedelta(days=1), tz) if to else None,
    )
    result, display = await factories.transactions(c).list(ctx, flt, cursor=cursor,
                                                           limit=limit, tz=tz)
    return {
        "items": [transaction_to_dict(t, display) for t in result.page.items],
        "next_cursor": result.page.next_cursor,
        "groups": [{"date": g.date, "net": g.net} for g in result.groups],
    }


@router.get("/{tx_id}", response_model=TransactionOut)
async def get_transaction(tx_id: UUID, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    tx, display = await factories.transactions(c).get(ctx, tx_id)
    return transaction_to_dict(tx, display)


@router.patch("/{tx_id}", response_model=TransactionOut)
async def update_transaction(tx_id: UUID, body: TransactionUpdateIn, ctx: AuthDep,
                             c: ContainerDep) -> dict[str, Any]:
    fields = body.model_dump(exclude_unset=True)
    cmd = UpdateTransactionCommand(**fields, fields=frozenset(fields))
    return transaction_to_dict(await factories.transactions(c).update(ctx, tx_id, cmd))


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(tx_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    """Soft delete (sync uchun). O'tkazmada ikkala yozuv ham o'chadi."""
    await factories.transactions(c).delete(ctx, tx_id)
