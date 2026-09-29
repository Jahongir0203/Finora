from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, StringConstraints

from app.presentation.schemas.common import StrictModel


class ReceiptItemOut(BaseModel):
    name: str
    quantity: float
    price: int


class ReceiptOut(BaseModel):
    receipt_id: UUID
    id: UUID
    source: str
    merchant: str | None
    total: int | None
    occurred_at: datetime | None
    items: list[ReceiptItemOut]
    suggested_category_id: str | None
    confidence: float
    has_image: bool
    confirmed: bool
    created_at: datetime


class ReceiptPageOut(BaseModel):
    items: list[ReceiptOut]
    next_cursor: str | None


class QrIn(StrictModel):
    payload: Annotated[str, StringConstraints(min_length=1, max_length=512)]


class SignedUrlOut(BaseModel):
    url: str
    expires_at: datetime
