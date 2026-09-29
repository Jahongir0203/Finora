from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.domain.categories.entities import CategoryType
from app.presentation.schemas.common import Amount, StrictModel

CategoryName = Annotated[str, StringConstraints(max_length=32)]
CategoryRef = Annotated[str, StringConstraints(min_length=2, max_length=36,
                                               pattern=r"^[a-z0-9\-]+$")]


class CategoryCreateIn(StrictModel):
    name: CategoryName
    icon: str
    color: str
    type: CategoryType
    monthly_limit: Amount | None = None


class CategoryUpdateIn(StrictModel):
    """Tizim kategoriyasida faqat monthly_limit va name (override) o'zgaradi."""

    name: CategoryName | None = None
    icon: str | None = None
    color: str | None = None
    monthly_limit: Amount | None = None


class CategoryDeleteIn(StrictModel):
    reassign_to: CategoryRef | None = None


class CategoryOut(BaseModel):
    id: str
    name: str
    icon: str
    color: str
    type: CategoryType
    is_system: bool
    monthly_limit: int | None
    spent: int
    transactions_count: int


class BudgetOut(BaseModel):
    category_id: str
    limit: int
    spent: int
    pct: int
    status: str
    left: int
