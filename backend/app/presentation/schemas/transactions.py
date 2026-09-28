from datetime import datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel

from app.domain.transactions.entities import TransactionKind
from app.presentation.schemas.common import Amount, Name, Note, StrictModel


class TransactionCreateIn(StrictModel):
    kind: TransactionKind
    amount: Amount
    category: Name
    occurred_at: AwareDatetime
    note: Note | None = None


class TransactionOut(BaseModel):
    id: UUID
    kind: TransactionKind
    amount: int
    category: str
    note: str | None
    occurred_at: datetime
    created_at: datetime


class ExportIn(StrictModel):
    since: AwareDatetime | None = None
    until: AwareDatetime | None = None


class ExportOut(BaseModel):
    download_url: str
    expires_at: datetime
