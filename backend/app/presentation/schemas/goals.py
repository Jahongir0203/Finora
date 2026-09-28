from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.presentation.schemas.common import Amount, Name, StrictModel


class GoalCreateIn(StrictModel):
    name: Name
    target_amount: Amount


class GoalUpdateIn(StrictModel):
    name: Name | None = None
    target_amount: Amount | None = None


class GoalEntryIn(StrictModel):
    amount: Amount


class GoalOut(BaseModel):
    id: UUID
    name: str
    target_amount: int
    saved: int
    created_at: datetime
