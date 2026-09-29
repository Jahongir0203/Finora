from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, StringConstraints

from app.domain.accounts.entities import AccountType, CardNetwork, OnboardingLocation
from app.presentation.schemas.common import Amount, Name, NonNegativeAmount, StrictModel, TxNote

Last4 = Annotated[str, StringConstraints(pattern=r"^\d{4}$")]
Expiry = Annotated[str, StringConstraints(pattern=r"^(0[1-9]|1[0-2])/\d{2}$")]
HexColor = Annotated[str, StringConstraints(pattern=r"^#[0-9A-Fa-f]{6}$")]


class AccountCreateIn(StrictModel):
    """To'liq karta raqami qabul qilinmaydi — faqat last4 va expiry."""

    type: AccountType
    name: Name | None = None
    bank_name: Name | None = None
    network: CardNetwork | None = None
    last4: Last4 | None = None
    expiry: Expiry | None = None
    color: HexColor | None = None
    opening_balance: NonNegativeAmount = 0
    monthly_limit: Amount | None = None
    is_default: bool = False


class AccountUpdateIn(StrictModel):
    name: Name | None = None
    bank_name: Name | None = None
    network: CardNetwork | None = None
    last4: Last4 | None = None
    expiry: Expiry | None = None
    color: HexColor | None = None
    opening_balance: NonNegativeAmount | None = None
    monthly_limit: Amount | None = None
    is_default: bool | None = None


class AccountOut(BaseModel):
    id: UUID
    type: AccountType
    name: str
    bank_name: str | None
    network: CardNetwork | None
    last4: str | None
    expiry: str | None
    color: str | None
    opening_balance: int
    monthly_limit: int | None
    frozen: bool
    is_default: bool
    balance: int
    balance_display: str | None = None
    display_currency: str | None = None
    created_at: datetime
    updated_at: datetime


class AccountListOut(BaseModel):
    total: int
    count: int
    items: list[AccountOut]
    total_display: str | None = None
    display_currency: str | None = None


class OnboardingBalanceIn(StrictModel):
    amount: NonNegativeAmount
    location: OnboardingLocation


class OnboardingBalanceOut(BaseModel):
    accounts: list[AccountOut]


class TransferIn(StrictModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: Amount
    note: TxNote | None = None
    occurred_at: AwareDatetime | None = None
