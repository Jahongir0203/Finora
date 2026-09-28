from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.common.values import ensure_amount, ensure_name


class Repeat(StrEnum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass(slots=True)
class Reminder:
    id: UUID
    user_id: UUID
    title: str
    due_at: datetime
    repeat: Repeat
    created_at: datetime
    amount: int | None = None

    def __post_init__(self) -> None:
        self.title = ensure_name(self.title)
        if self.amount is not None:
            ensure_amount(self.amount)
