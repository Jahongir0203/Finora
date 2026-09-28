from datetime import datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel

from app.domain.reminders.entities import Repeat
from app.presentation.schemas.common import Amount, Name, StrictModel


class ReminderCreateIn(StrictModel):
    title: Name
    due_at: AwareDatetime
    repeat: Repeat = Repeat.NONE
    amount: Amount | None = None


class ReminderUpdateIn(StrictModel):
    title: Name | None = None
    due_at: AwareDatetime | None = None
    repeat: Repeat | None = None
    amount: Amount | None = None


class ReminderOut(BaseModel):
    id: UUID
    title: str
    amount: int | None
    due_at: datetime
    repeat: Repeat
    created_at: datetime
