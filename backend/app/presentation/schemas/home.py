from datetime import date
from uuid import UUID

from pydantic import BaseModel

from app.presentation.schemas.transactions import TransactionOut


class HomeUserOut(BaseModel):
    first_name: str | None
    initials: str


class HomeBalanceOut(BaseModel):
    total: int
    currency: str
    need_balance: bool
    total_display: str | None = None
    display_currency: str | None = None


class HomeMonthOut(BaseModel):
    income: int
    expenses: int
    income_display: str | None = None
    expenses_display: str | None = None


class GetStartedOut(BaseModel):
    balance: bool
    transaction: bool
    goal: bool
    reminder: bool


class AiTeaserOut(BaseModel):
    title: str
    saving: int


class BudgetSummaryOut(BaseModel):
    month: str
    spent: int
    limit: int


class UpcomingPaymentOut(BaseModel):
    id: UUID
    title: str
    amount: int
    due_date: date
    category_id: str


class HomeOut(BaseModel):
    user: HomeUserOut
    balance: HomeBalanceOut
    month: HomeMonthOut
    unread_notifications: int
    get_started: GetStartedOut
    ai_teaser: AiTeaserOut | None
    budget_summary: BudgetSummaryOut | None
    upcoming_payments: list[UpcomingPaymentOut]
    recent_transactions: list[TransactionOut]
