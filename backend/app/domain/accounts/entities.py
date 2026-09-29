"""Hisoblar va kartalar (BE-1401).

To'liq karta raqami saqlanmaydi va qabul qilinmaydi — faqat `last4` va `expiry`.
Balans saqlanmaydi: opening_balance + tranzaksiyalar + goal yozuvlaridan hisoblanadi.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.common.errors import ValidationFailedError
from app.domain.common.values import MAX_AMOUNT, ensure_amount, ensure_name


class AccountType(StrEnum):
    CARD = "card"
    CASH = "cash"
    BANK_ACCOUNT = "bank_account"


class CardNetwork(StrEnum):
    UZCARD = "UZCARD"
    HUMO = "HUMO"
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"


class OnboardingLocation(StrEnum):
    CASH = "cash"
    CARD = "card"
    BOTH = "both"


_LAST4 = re.compile(r"^\d{4}$")
_EXPIRY = re.compile(r"^(0[1-9]|1[0-2])/\d{2}$")
_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def ensure_opening_balance(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_AMOUNT:
        raise ValidationFailedError("Boshlang'ich balans 0..10^12", fields=["opening_balance"])
    return value


@dataclass(slots=True)
class Account:
    id: UUID
    user_id: UUID
    type: AccountType
    name: str
    opening_balance: int
    created_at: datetime
    updated_at: datetime
    bank_name: str | None = None
    network: CardNetwork | None = None
    last4: str | None = None
    expiry: str | None = None
    color: str | None = None
    monthly_limit: int | None = None
    frozen: bool = False
    is_default: bool = False
    archived_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.name = ensure_name(self.name)
        ensure_opening_balance(self.opening_balance)
        if self.bank_name is not None:
            self.bank_name = ensure_name(self.bank_name)
        if self.last4 is not None and not _LAST4.fullmatch(self.last4):
            raise ValidationFailedError("last4 — 4 ta raqam", fields=["last4"])
        if self.expiry is not None and not _EXPIRY.fullmatch(self.expiry):
            raise ValidationFailedError("expiry MM/YY formatida", fields=["expiry"])
        if self.color is not None and not _COLOR.fullmatch(self.color):
            raise ValidationFailedError("color #RRGGBB formatida", fields=["color"])
        if self.monthly_limit is not None:
            ensure_amount(self.monthly_limit)
        if self.type is not AccountType.CARD and (self.network or self.last4 or self.expiry):
            raise ValidationFailedError("Karta maydonlari faqat card turida",
                                        fields=["network", "last4", "expiry"])

    @property
    def is_active(self) -> bool:
        return self.archived_at is None
