from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.presentation.schemas.common import Amount, Name, StrictModel


class BudgetCreateIn(StrictModel):
    category: Name
    monthly_limit: Amount


class BudgetUpdateIn(StrictModel):
    monthly_limit: Amount


class BudgetOut(BaseModel):
    id: UUID
    category: str
    monthly_limit: int
    spent: int
    remaining: int
    created_at: datetime
