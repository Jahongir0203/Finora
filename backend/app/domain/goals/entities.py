"""Jamg'arma maqsadlari (BE-1101..1105).

`saved` saqlanmaydi — faqat serverda deposit/withdraw yozuvlaridan hisoblanadi.
Har bir yozuv hisobga bog'langan: deposit hisob balansini kamaytiradi, withdraw oshiradi.
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from app.domain.common.errors import InsufficientFundsError, ValidationFailedError
from app.domain.common.values import MAX_NAME_LENGTH, ensure_amount

MIN_GOAL_TARGET = 100_000
MILESTONES = (25, 50, 75, 100)
DEFAULT_GOAL_ICON = "target"


class EntryKind(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class EntrySource(StrEnum):
    MANUAL = "manual"
    AUTO = "auto"  # auto-save (BE-1105)
    CLOSE = "close"  # goal o'chirilganda qoldiq hisobga qaytadi (BE-1103)


def ensure_goal_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValidationFailedError(fields=["name"], code="goal_name_required")
    if len(value) > MAX_NAME_LENGTH:
        raise ValidationFailedError("Nom 64 belgidan oshmasin", fields=["name"])
    return value


def ensure_goal_target(value: int) -> int:
    ensure_amount(value)
    if value < MIN_GOAL_TARGET:
        raise ValidationFailedError(fields=["target"], code="goal_target_min")
    return value


@dataclass(slots=True)
class Goal:
    id: UUID
    user_id: UUID
    name: str
    target_amount: int
    created_at: datetime
    updated_at: datetime | None = None
    icon: str = DEFAULT_GOAL_ICON
    deadline: date | None = None
    auto_save_monthly: int | None = None
    auto_save_day: int = 1
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()
        if self.updated_at is None:
            self.updated_at = self.created_at

    def validate(self) -> None:
        self.name = ensure_goal_name(self.name)
        ensure_goal_target(self.target_amount)
        if not self.icon or len(self.icon) > 32:
            raise ValidationFailedError("Ikon noto'g'ri", fields=["icon"])
        if self.auto_save_monthly is not None:
            ensure_amount(self.auto_save_monthly)
        if not 1 <= self.auto_save_day <= 28:
            raise ValidationFailedError("auto_save_day 1..28", fields=["auto_save_day"])


@dataclass(slots=True)
class GoalEntry:
    id: UUID
    goal_id: UUID
    user_id: UUID
    kind: EntryKind
    amount: int
    created_at: datetime
    account_id: UUID | None = None
    source: EntrySource = EntrySource.MANUAL
    # Auto-save idempotentligi: "auto:2026-09" (goal_id bilan unique)
    dedupe_key: str | None = None

    def __post_init__(self) -> None:
        ensure_amount(self.amount)

    @property
    def signed(self) -> int:
        return self.amount if self.kind is EntryKind.DEPOSIT else -self.amount


def ensure_can_withdraw(saved: int, amount: int) -> None:
    """Goal balansi faqat serverda, yozuvlardan hisoblanadi (02-backend.md, 3-bo'lim)."""
    ensure_amount(amount)
    if amount > saved:
        raise InsufficientFundsError()


def progress_pct(saved: int, target: int) -> int:
    return min(100, saved * 100 // target) if target > 0 else 0


def crossed_milestones(before: int, after: int, target: int) -> list[int]:
    b, a = progress_pct(before, target), progress_pct(after, target)
    return [m for m in MILESTONES if b < m <= a]


def months_between(start: date, end: date) -> int:
    """To'liq bo'lmagan oy ham hisoblanadi (kamida 1)."""
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day > start.day:
        months += 1
    return max(1, months)


def ceil_div(a: int, b: int) -> int:
    return -(-a // b)


@dataclass(frozen=True, slots=True)
class GoalPlan:
    remaining: int
    monthly_needed: int | None
    eta_months: int | None


def plan(target: int, saved: int, today: date, deadline: date | None,
         auto_save: int | None) -> GoalPlan:
    """BE-1104: monthly_needed = ceil(qoldiq / oylar), eta_months = ceil(qoldiq / auto_save)."""
    remaining = max(0, target - saved)
    monthly = (ceil_div(remaining, months_between(today, deadline))
               if deadline and deadline > today and remaining else None)
    eta = ceil_div(remaining, auto_save) if auto_save and remaining else None
    return GoalPlan(remaining=remaining, monthly_needed=monthly,
                    eta_months=0 if remaining == 0 else eta)
