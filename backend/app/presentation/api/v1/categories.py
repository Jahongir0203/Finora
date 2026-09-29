from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Query, status

from app.domain.categories.entities import CategoryType
from app.domain.common.errors import ValidationFailedError
from app.domain.common.time import parse_month
from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey, TzDep
from app.presentation.schemas.categories import (
    BudgetOut,
    CategoryCreateIn,
    CategoryDeleteIn,
    CategoryOut,
    CategoryRef,
    CategoryUpdateIn,
)
from app.presentation.schemas.common import ERROR_RESPONSES

router = APIRouter(prefix="/categories", tags=["categories"], responses=ERROR_RESPONSES)
budgets_router = APIRouter(prefix="/budgets", tags=["budgets"], responses=ERROR_RESPONSES)


@router.get("", response_model=list[CategoryOut])
async def list_categories(ctx: AuthDep, c: ContainerDep, tz: TzDep,
                          type: CategoryType | None = None) -> list[dict[str, Any]]:
    """Tizim + user kategoriyalari, har birida joriy oy `spent` (BE-1501)."""
    return await factories.categories(c).list(ctx, tz, type)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryOut)
async def create_category(body: CategoryCreateIn, ctx: AuthDep, c: ContainerDep,
                          idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    return await factories.categories(c).create(ctx, body.name, body.icon, body.color,
                                                body.type, body.monthly_limit, idempotency_key)


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(category_id: CategoryRef, body: CategoryUpdateIn, ctx: AuthDep,
                          c: ContainerDep) -> dict[str, Any]:
    """`monthly_limit: null` — limitni olib tashlash (BE-1001)."""
    return await factories.categories(c).update(ctx, category_id,
                                                **body.model_dump(exclude_unset=True))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: CategoryRef, ctx: AuthDep, c: ContainerDep,
                          body: CategoryDeleteIn | None = None) -> None:
    """Faqat user kategoriyasi. Tranzaksiyalari bo'lsa `reassign_to` majburiy (409)."""
    await factories.categories(c).delete(ctx, category_id, body.reassign_to if body else None)


@budgets_router.get("", response_model=list[BudgetOut])
async def list_budgets(ctx: AuthDep, c: ContainerDep, tz: TzDep,
                       month: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")] = None,
                       ) -> list[dict[str, Any]]:
    """Limit qo'yilgan kategoriyalar: warning 0.75 ≤ pct ≤ 1, over pct > 1 (BE-1001)."""
    parsed: date | None = None
    if month is not None:
        try:
            parsed = parse_month(month)
        except ValueError:
            raise ValidationFailedError(fields=["month"]) from None
    return await factories.categories(c).budgets(ctx, parsed, tz, c.clock.now())
