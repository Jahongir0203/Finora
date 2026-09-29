from datetime import date, datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.transactions.entities import TransactionType
from app.presentation.schemas.categories import CategoryRef
from app.presentation.schemas.common import Amount, LooseName, StrictModel, TxNote


class TransactionCreateIn(StrictModel):
    type: TransactionType
    amount: Amount
    category_id: CategoryRef
    title: LooseName | None = None
    note: TxNote | None = None
    account_id: UUID | None = None
    occurred_at: AwareDatetime | None = None
    receipt_id: UUID | None = None
    # Offline yaratilgan yozuv (BE-302): mijozdagi yaratilish vaqti
    client_created_at: AwareDatetime | None = None


class TransactionUpdateIn(StrictModel):
    amount: Amount | None = None
    category_id: CategoryRef | None = None
    title: LooseName | None = None
    note: TxNote | None = None
    account_id: UUID | None = None
    occurred_at: AwareDatetime | None = None


class TransactionOut(BaseModel):
    id: UUID
    type: TransactionType
    amount: int
    currency: str
    category_id: str
    account_id: UUID
    title: str | None
    note: str | None
    source: str
    receipt_id: UUID | None
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime
    transfer_peer_id: UUID | None
    direction: str | None
    amount_display: str | None = None
    display_currency: str | None = None


class BalanceOut(BaseModel):
    total: int


class TransactionCreatedOut(BaseModel):
    transaction: TransactionOut
    balance: BalanceOut


class DayGroupOut(BaseModel):
    date: date
    net: int


class TransactionPageOut(BaseModel):
    items: list[TransactionOut]
    next_cursor: str | None
    groups: list[DayGroupOut]


class TransferOut(BaseModel):
    out: TransactionOut
    in_: TransactionOut = Field(alias="in")

    model_config = ConfigDict(populate_by_name=True)
