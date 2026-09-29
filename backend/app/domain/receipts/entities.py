"""Cheklar (BE-701..703). Rasm yopiq omborda; ochish faqat 5 daqiqalik imzolangan URL orqali.

Tranzaksiyaga bog'lanmagan (tasdiqlanmagan) cheklar 24 soatdan keyin o'chiriladi.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class ReceiptSource(StrEnum):
    IMAGE = "image"
    QR = "qr"


@dataclass(frozen=True, slots=True)
class ReceiptItem:
    name: str
    quantity: float
    price: int

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "quantity": self.quantity, "price": self.price}


@dataclass(slots=True)
class ParsedReceipt:
    """OCR yoki fiskal QR natijasi. Summalar so'mda."""

    merchant: str | None
    total: int | None
    occurred_at: datetime | None
    items: list[ReceiptItem] = field(default_factory=list)
    confidence: float = 0.0


@dataclass(slots=True)
class Receipt:
    id: UUID
    user_id: UUID
    created_at: datetime
    source: ReceiptSource = ReceiptSource.IMAGE
    file_key: str | None = None
    content_type: str | None = None
    size_bytes: int | None = None
    merchant: str | None = None
    total: int | None = None
    occurred_at: datetime | None = None
    items: list[ReceiptItem] = field(default_factory=list)
    suggested_category_id: str | None = None
    confidence: float = 0.0
    confirmed_at: datetime | None = None
    # Fiskal chek belgisi (QR): bitta chekni ikki marta saqlamaslik uchun
    fiscal_sign: str | None = None
