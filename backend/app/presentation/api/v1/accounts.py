from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.application.accounts.use_cases import AccountInput
from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey
from app.presentation.schemas.accounts import (
    AccountCreateIn,
    AccountListOut,
    AccountOut,
    AccountUpdateIn,
    TransferIn,
)
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.transactions import TransferOut

router = APIRouter(prefix="/accounts", tags=["accounts"], responses=ERROR_RESPONSES)
transfers_router = APIRouter(prefix="/transfers", tags=["accounts"], responses=ERROR_RESPONSES)


@router.get("", response_model=AccountListOut)
async def list_accounts(ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return await factories.accounts(c).list(ctx)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountOut)
async def create_account(body: AccountCreateIn, ctx: AuthDep, c: ContainerDep,
                         idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    return await factories.accounts(c).create(ctx, AccountInput(**body.model_dump()),
                                              idempotency_key)


@router.get("/{account_id}", response_model=AccountOut)
async def get_account(account_id: UUID, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return await factories.accounts(c).get(ctx, account_id)


@router.patch("/{account_id}", response_model=AccountOut)
async def update_account(account_id: UUID, body: AccountUpdateIn, ctx: AuthDep,
                         c: ContainerDep) -> dict[str, Any]:
    return await factories.accounts(c).update(ctx, account_id,
                                              body.model_dump(exclude_unset=True))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    """Tranzaksiyasi bor hisob arxivlanadi, bo'sh hisob o'chiriladi."""
    await factories.accounts(c).delete(ctx, account_id)


@router.post("/{account_id}/freeze", status_code=status.HTTP_204_NO_CONTENT)
async def freeze(account_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    """Faqat Finora ichidagi belgi: muzlatilgan hisobga yangi yozuv tushmaydi (BE-1403)."""
    await factories.accounts(c).set_frozen(ctx, account_id, True)


@router.post("/{account_id}/unfreeze", status_code=status.HTTP_204_NO_CONTENT)
async def unfreeze(account_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await factories.accounts(c).set_frozen(ctx, account_id, False)


@transfers_router.post("", status_code=status.HTTP_201_CREATED, response_model=TransferOut)
async def create_transfer(body: TransferIn, ctx: AuthDep, c: ContainerDep,
                          idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    """Ikki bog'langan transfer yozuvi; statistikada xarajat emas (BE-1404)."""
    return await factories.transfers(c).create(
        ctx, body.from_account_id, body.to_account_id, body.amount, body.note,
        body.occurred_at, idempotency_key)
