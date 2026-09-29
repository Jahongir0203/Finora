"""To'lov eslatmalari (BE-1201..1203)."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum
from uuid import UUID

from app.domain.common.time import add_months
from app.domain.common.values import ensure_amount, ensure_name


class Repeat(StrEnum):
    ONCE = "once"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass(slots=True)
class Reminder:
    id: UUID
    user_id: UUID
    title: str
    category_id: str
    amount: int
    next_due_date: date
    repeat: Repeat
    created_at: datetime
    updated_at: datetime | None = None
    enabled: bool = True
    # Oyning asl kuni: 31-sanali eslatma fevralda 28 ga tushadi, martda yana 31 ga qaytadi
    anchor_day: int | None = None
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        self.title = ensure_name(self.title)
        ensure_amount(self.amount)
        if self.anchor_day is None:
            self.anchor_day = self.next_due_date.day
        if self.updated_at is None:
            self.updated_at = self.created_at

    def due_in_days(self, today: date) -> int:
        return (self.next_due_date - today).days

    def following_date(self) -> date | None:
        """Keyingi sana; `once` uchun None."""
        d = self.next_due_date
        if self.repeat is Repeat.WEEKLY:
            return d + timedelta(days=7)
        if self.repeat is Repeat.MONTHLY:
            return add_months(d, 1, self.anchor_day)
        if self.repeat is Repeat.YEARLY:
            return add_months(d, 12, self.anchor_day)
        return None

    def advance(self, today: date) -> bool:
        """Sana o'tgan bo'lsa suradi (BE-1202). `once` — o'chiriladi. O'zgarsa True."""
        changed = False
        while self.enabled and self.next_due_date < today:
            nxt = self.following_date()
            if nxt is None:
                self.enabled = False
            else:
                self.next_due_date = nxt
            changed = True
        return changed

    def mark_paid(self) -> None:
        """BE-1203: to'landi — keyingi sanaga suriladi (`once` o'chadi)."""
        nxt = self.following_date()
        if nxt is None:
            self.enabled = False
        else:
            self.next_due_date = nxt
