from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.budgets.entities import Budget
from app.domain.common.errors import ConflictError
from app.infrastructure.db.models import BudgetModel


def _budget(m: BudgetModel) -> Budget:
    return Budget(id=m.id, user_id=m.user_id, category=m.category,
                  monthly_limit=m.monthly_limit, created_at=m.created_at)


class SqlBudgetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, budget: Budget) -> None:
        self._s.add(BudgetModel(id=budget.id, user_id=budget.user_id, category=budget.category,
                                monthly_limit=budget.monthly_limit, created_at=budget.created_at))
        try:
            await self._s.flush()
        except IntegrityError:
            raise ConflictError("Bu kategoriya uchun byudjet allaqachon bor") from None

    async def get_for_user(self, user_id: UUID, budget_id: UUID) -> Budget | None:
        m = await self._s.scalar(
            select(BudgetModel).where(BudgetModel.id == budget_id, BudgetModel.user_id == user_id)
        )
        return _budget(m) if m else None

    async def list_for_user(self, user_id: UUID) -> list[Budget]:
        rows = await self._s.scalars(
            select(BudgetModel).where(BudgetModel.user_id == user_id)
            .order_by(BudgetModel.category)
        )
        return [_budget(m) for m in rows]

    async def update(self, budget: Budget) -> None:
        await self._s.execute(
            update(BudgetModel)
            .where(BudgetModel.id == budget.id, BudgetModel.user_id == budget.user_id)
            .values(monthly_limit=budget.monthly_limit)
        )

    async def delete_for_user(self, user_id: UUID, budget_id: UUID) -> bool:
        result = await self._s.execute(
            delete(BudgetModel).where(BudgetModel.id == budget_id, BudgetModel.user_id == user_id)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]
