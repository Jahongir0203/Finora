"""Byudjetlar. Sarflangan summa faqat serverda, joriy oy tranzaksiyalaridan hisoblanadi."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import Clock
from app.application.common.uow import UnitOfWork
from app.core.config import Settings
from app.domain.budgets.entities import Budget, month_bounds
from app.domain.common.errors import NotFoundError
from app.domain.common.ids import uuid7
from app.domain.common.values import ensure_amount


@dataclass(frozen=True, slots=True)
class BudgetView:
    id: UUID
    category: str
    monthly_limit: int
    spent: int
    created_at: datetime

    @property
    def remaining(self) -> int:
        return self.monthly_limit - self.spent

    def to_dict(self) -> dict[str, Any]:
        return {"id": str(self.id), "category": self.category,
                "monthly_limit": self.monthly_limit, "spent": self.spent,
                "remaining": self.remaining, "created_at": self.created_at.isoformat()}


class BudgetService:
    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings

    async def _spent(self, uow: UnitOfWork, user_id: UUID) -> dict[str, int]:
        since, until = month_bounds(self._clock.now())
        return await uow.transactions.totals_by_category(user_id, since, until)

    @staticmethod
    def _view(b: Budget, spent: dict[str, int]) -> BudgetView:
        return BudgetView(b.id, b.category, b.monthly_limit, spent.get(b.category, 0),
                          b.created_at)

    async def create(self, ctx: AuthContext, category: str, monthly_limit: int,
                     idempotency_key: str | None) -> dict[str, Any]:
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                budget = Budget(uuid7(), ctx.user_id, category, monthly_limit, self._clock.now())
                await uow.budgets.add(budget)
                return self._view(budget, await self._spent(uow, ctx.user_id)).to_dict()

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="budget.create",
                payload={"category": category, "monthly_limit": monthly_limit},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )

    async def list(self, ctx: AuthContext) -> list[BudgetView]:
        async with self._uow as uow:
            budgets = await uow.budgets.list_for_user(ctx.user_id)
            spent = await self._spent(uow, ctx.user_id)
        return [self._view(b, spent) for b in budgets]

    async def get(self, ctx: AuthContext, budget_id: UUID) -> BudgetView:
        async with self._uow as uow:
            budget = await uow.budgets.get_for_user(ctx.user_id, budget_id)
            if budget is None:
                raise NotFoundError()
            return self._view(budget, await self._spent(uow, ctx.user_id))

    async def update(self, ctx: AuthContext, budget_id: UUID, monthly_limit: int) -> BudgetView:
        async with self._uow as uow:
            budget = await uow.budgets.get_for_user(ctx.user_id, budget_id)
            if budget is None:
                raise NotFoundError()
            budget.monthly_limit = ensure_amount(monthly_limit)
            await uow.budgets.update(budget)
            view = self._view(budget, await self._spent(uow, ctx.user_id))
            await uow.commit()
            return view

    async def delete(self, ctx: AuthContext, budget_id: UUID) -> None:
        async with self._uow as uow:
            if not await uow.budgets.delete_for_user(ctx.user_id, budget_id):
                raise NotFoundError()
            await uow.commit()
