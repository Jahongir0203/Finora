from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, StringConstraints

from app.domain.insights.entities import InsightAction, InsightKind, InsightStatus
from app.presentation.schemas.common import Amount, StrictModel

Question = Annotated[str, StringConstraints(min_length=1, max_length=300)]


class AskIn(StrictModel):
    question: Question


class AskOut(BaseModel):
    answer: str
    window_days: int


class InsightOut(BaseModel):
    id: UUID
    kind: InsightKind
    icon: str
    category_id: str | None
    title: str
    body: str
    saving: int | None
    action: InsightAction
    status: InsightStatus


class InsightListOut(BaseModel):
    potential_saving: int
    items: list[InsightOut]


class InsightActionIn(StrictModel):
    """set_budget: limit (ixtiyoriy); turn_on_autosave: goal_id, amount (ixtiyoriy)."""

    limit: Amount | None = None
    goal_id: UUID | None = None
    amount: Amount | None = None


class InsightActionOut(BaseModel):
    status: InsightStatus
    category_id: str | None = None
    monthly_limit: int | None = None
    reminder_id: UUID | None = None
    goal_id: UUID | None = None
    auto_save_monthly: int | None = None


class SuggestionsOut(BaseModel):
    items: list[str]


