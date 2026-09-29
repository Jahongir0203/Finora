"""Tranzaksiyalar (BE-501).

Summa har doim musbat, yo'nalish `type` (va o'tkazmada `direction`) bilan beriladi.
O'tkazma — ikki bog'langan yozuv (out/in), statistikada xarajat emas (BE-1404).
O'chirish soft delete: `deleted_at` (offline sync uchun, BE-302).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.common.errors import ValidationFailedError
from app.domain.common.values import MAX_NAME_LENGTH, ensure_amount

MAX_TX_NOTE_LENGTH = 256


class TransactionType(StrEnum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"


# Eski nom (tashqi modullar uchun)
TransactionKind = TransactionType


class TransactionSource(StrEnum):
    MANUAL = "manual"
    SCAN = "scan"
    BANK = "bank"


class TransferDirection(StrEnum):
    OUT = "out"
    IN = "in"


@dataclass(slots=True)
class Transaction:
    id: UUID
    user_id: UUID
    account_id: UUID
    type: TransactionType
    amount: int
    category_id: str
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime
    title: str | None = None
    note: str | None = None
    source: TransactionSource = TransactionSource.MANUAL
    receipt_id: UUID | None = None
    currency: str = "UZS"
    client_created_at: datetime | None = None
    transfer_peer_id: UUID | None = None
    direction: TransferDirection | None = None
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        ensure_amount(self.amount)
        if self.title is not None:
            self.title = self.title.strip() or None
            if self.title and len(self.title) > MAX_NAME_LENGTH:
                raise ValidationFailedError("Nom 64 belgidan oshmasin", fields=["title"])
        if self.note is not None and len(self.note) > MAX_TX_NOTE_LENGTH:
            raise ValidationFailedError("Izoh 256 belgidan oshmasin", fields=["note"])
        if (self.type is TransactionType.TRANSFER) != (self.direction is not None):
            raise ValidationFailedError("direction faqat transfer uchun", fields=["type"])

    @property
    def signed_amount(self) -> int:
        """Hisob balansiga ta'siri."""
        if self.type is TransactionType.INCOME or self.direction is TransferDirection.IN:
            return self.amount
        return -self.amount
