from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.common.errors import InsufficientFundsError
from app.domain.common.values import ensure_amount, ensure_name


class EntryKind(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


@dataclass(slots=True)
class Goal:
    id: UUID
    user_id: UUID
    name: str
    target_amount: int
    created_at: datetime

    def __post_init__(self) -> None:
        self.name = ensure_name(self.name)
        ensure_amount(self.target_amount)


@dataclass(slots=True)
class GoalEntry:
    id: UUID
    goal_id: UUID
    user_id: UUID
    kind: EntryKind
    amount: int
    created_at: datetime

    def __post_init__(self) -> None:
        ensure_amount(self.amount)


def ensure_can_withdraw(saved: int, amount: int) -> None:
    """Goal balansi faqat serverda, yozuvlardan hisoblanadi (02-backend.md, 3-bo'lim)."""
    ensure_amount(amount)
    if amount > saved:
        raise InsufficientFundsError()
