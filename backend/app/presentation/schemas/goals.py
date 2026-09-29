from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

from app.domain.goals.entities import EntryKind, EntrySource
from app.presentation.schemas.common import Amount, LooseName, StrictModel

Icon = Annotated[str, StringConstraints(min_length=1, max_length=32,
                                        pattern=r"^[a-z0-9\-]+$")]
SaveDay = Annotated[int, Field(ge=1, le=28)]


class GoalCreateIn(StrictModel):
    name: LooseName
    icon: Icon | None = None
    target: Amount
    deadline: date | None = None
    auto_save_monthly: Amount | None = None
    auto_save_day: SaveDay = 1


class GoalUpdateIn(StrictModel):
    name: LooseName | None = None
    icon: Icon | None = None
    target: Amount | None = None
    deadline: date | None = None
    auto_save_monthly: Amount | None = None
    auto_save_day: SaveDay | None = None


class GoalEntryIn(StrictModel):
    amount: Amount
    account_id: UUID | None = None


class GoalPlanOut(BaseModel):
    remaining: int
    monthly_needed: int | None
    eta_months: int | None


class GoalOut(BaseModel):
    id: UUID
    name: str
    icon: str
    target: int
    saved: int
    pct: int
    deadline: date | None
    auto_save_monthly: int | None
    auto_save_day: int
    created_at: datetime
    plan: GoalPlanOut


class GoalDeletedOut(BaseModel):
    returned_amount: int


class GoalEntryOut(BaseModel):
    id: UUID
    kind: EntryKind
    amount: int
    account_id: UUID | None
    source: EntrySource
    created_at: datetime


class GoalHistoryOut(BaseModel):
    items: list[GoalEntryOut]
    next_cursor: str | None
