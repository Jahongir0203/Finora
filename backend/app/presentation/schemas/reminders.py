from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.reminders.entities import Repeat
from app.presentation.schemas.categories import CategoryRef
from app.presentation.schemas.common import Amount, Name, StrictModel
from app.presentation.schemas.transactions import TransactionOut


class ReminderCreateIn(StrictModel):
    title: Name
    category_id: CategoryRef
    amount: Amount
    due_date: date
    repeat: Repeat = Repeat.MONTHLY


class ReminderUpdateIn(StrictModel):
    title: Name | None = None
    category_id: CategoryRef | None = None
    amount: Amount | None = None
    due_date: date | None = None
    repeat: Repeat | None = None
    enabled: bool | None = None


class ReminderPayIn(StrictModel):
    account_id: UUID | None = None


class ReminderOut(BaseModel):
    id: UUID
    title: str
    category_id: str
    amount: int
    next_due_date: date
    repeat: Repeat
    enabled: bool
    due_in_days: int
    created_at: datetime


class ReminderPaidOut(BaseModel):
    transaction: TransactionOut
    reminder: ReminderOut
