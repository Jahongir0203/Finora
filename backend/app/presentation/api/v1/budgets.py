from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.application.budgets.use_cases import BudgetService
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey
from app.presentation.schemas.budgets import BudgetCreateIn, BudgetOut, BudgetUpdateIn

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _svc(c: ContainerDep) -> BudgetService:
    return BudgetService(c.uow(), c.clock, c.settings)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BudgetOut)
async def create_budget(body: BudgetCreateIn, ctx: AuthDep, c: ContainerDep,
                        idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    return await _svc(c).create(ctx, body.category, body.monthly_limit, idempotency_key)


@router.get("", response_model=list[BudgetOut])
async def list_budgets(ctx: AuthDep, c: ContainerDep) -> list[dict[str, Any]]:
    return [v.to_dict() for v in await _svc(c).list(ctx)]


@router.get("/{budget_id}", response_model=BudgetOut)
async def get_budget(budget_id: UUID, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return (await _svc(c).get(ctx, budget_id)).to_dict()


@router.patch("/{budget_id}", response_model=BudgetOut)
async def update_budget(budget_id: UUID, body: BudgetUpdateIn, ctx: AuthDep,
                        c: ContainerDep) -> dict[str, Any]:
    return (await _svc(c).update(ctx, budget_id, body.monthly_limit)).to_dict()


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(budget_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await _svc(c).delete(ctx, budget_id)
