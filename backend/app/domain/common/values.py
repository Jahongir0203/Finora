"""Qiymat obyektlari va umumiy invariantlar (02-backend.md, 4-bo'lim)."""

import re
from dataclasses import dataclass

from app.domain.common.errors import ValidationFailedError

MAX_AMOUNT = 10**12
MAX_NAME_LENGTH = 64
MAX_NOTE_LENGTH = 255


def ensure_amount(value: int) -> int:
    """Summa butun son (so'm), 0 < x <= 10^12."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationFailedError("Summa butun son bo'lishi kerak")
    if not 0 < value <= MAX_AMOUNT:
        raise ValidationFailedError("Summa 0 dan katta va 10^12 dan oshmasligi kerak")
    return value


def ensure_name(value: str, max_length: int = MAX_NAME_LENGTH) -> str:
    value = value.strip()
    if not value or len(value) > max_length:
        raise ValidationFailedError(f"Nom 1..{max_length} belgi bo'lishi kerak")
    return value


_UZ_PHONE_RE = re.compile(r"^\+998\d{9}$")


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    """E.164 formatidagi O'zbekiston raqami."""

    value: str

    def __post_init__(self) -> None:
        if not _UZ_PHONE_RE.fullmatch(self.value):
            raise ValidationFailedError("Telefon raqami +998XXXXXXXXX formatida bo'lishi kerak")

    @classmethod
    def parse(cls, raw: str) -> "PhoneNumber":
        digits = re.sub(r"[\s\-()]", "", raw)
        if not digits.startswith("+"):
            digits = "+" + digits
        return cls(digits)

    def masked(self) -> str:
        v = self.value
        return f"{v[:4]} {v[4:6]} *** ** {v[-2:]}"

    def __repr__(self) -> str:  # tasodifan logga tushsa ham to'liq raqam chiqmasin
        return f"PhoneNumber({self.masked()})"

    __str__ = __repr__
