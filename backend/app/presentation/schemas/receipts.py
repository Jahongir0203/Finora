from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReceiptOut(BaseModel):
    id: UUID
    content_type: str
    size_bytes: int
    created_at: datetime


class SignedUrlOut(BaseModel):
    url: str
    expires_at: datetime
