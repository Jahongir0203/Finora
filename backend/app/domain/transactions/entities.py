from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.common.errors import ValidationFailedError
from app.domain.common.values import MAX_NOTE_LENGTH, ensure_amount, ensure_name


class TransactionKind(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass(slots=True)
class Transaction:
    id: UUID
    user_id: UUID
    kind: TransactionKind
    amount: int
    category: str
    occurred_at: datetime
    created_at: datetime
    note: str | None = None

    def __post_init__(self) -> None:
        ensure_amount(self.amount)
        self.category = ensure_name(self.category)
        if self.note is not None and len(self.note) > MAX_NOTE_LENGTH:
            raise ValidationFailedError(f"Izoh {MAX_NOTE_LENGTH} belgidan oshmasligi kerak")
