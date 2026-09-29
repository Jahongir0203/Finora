from types import TracebackType
from typing import Protocol, Self

from app.application.common.idempotency import IdempotencyRepository
from app.domain.accounts.repository import AccountRepository
from app.domain.audit.repository import AuditRepository
from app.domain.auth.repository import (
    DeviceRepository,
    RefreshTokenRepository,
    SessionRepository,
)
from app.domain.categories.repository import CategoryRepository
from app.domain.currencies.repository import CurrencyRateRepository
from app.domain.exports.repository import ExportRepository
from app.domain.goals.repository import GoalRepository
from app.domain.help.repository import FaqRepository
from app.domain.insights.repository import InsightRepository
from app.domain.notifications.repository import NotificationRepository, PushTokenRepository
from app.domain.receipts.repository import ReceiptRepository
from app.domain.reminders.repository import ReminderRepository
from app.domain.transactions.repository import LedgerQueries, TransactionRepository
from app.domain.users.repository import UserRepository


class UnitOfWork(Protocol):
    users: UserRepository
    devices: DeviceRepository
    sessions: SessionRepository
    refresh_tokens: RefreshTokenRepository
    goals: GoalRepository
    transactions: TransactionRepository
    exports: ExportRepository
    receipts: ReceiptRepository
    reminders: ReminderRepository
    accounts: AccountRepository
    categories: CategoryRepository
    ledger: LedgerQueries
    insights: InsightRepository
    faq: FaqRepository
    currency_rates: CurrencyRateRepository
    notifications: NotificationRepository
    push_tokens: PushTokenRepository
    audit: AuditRepository
    idempotency: IdempotencyRepository

    async def __aenter__(self) -> Self: ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
