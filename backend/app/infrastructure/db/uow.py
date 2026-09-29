from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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
from app.infrastructure.db.repositories.accounts import SqlAccountRepository
from app.infrastructure.db.repositories.audit import SqlAuditRepository
from app.infrastructure.db.repositories.auth import (
    SqlDeviceRepository,
    SqlRefreshTokenRepository,
    SqlSessionRepository,
)
from app.infrastructure.db.repositories.categories import SqlCategoryRepository
from app.infrastructure.db.repositories.currencies import SqlCurrencyRateRepository
from app.infrastructure.db.repositories.exports import SqlExportRepository
from app.infrastructure.db.repositories.goals import SqlGoalRepository
from app.infrastructure.db.repositories.help import SqlFaqRepository
from app.infrastructure.db.repositories.idempotency import SqlIdempotencyRepository
from app.infrastructure.db.repositories.insights import SqlInsightRepository
from app.infrastructure.db.repositories.notifications import (
    SqlNotificationRepository,
    SqlPushTokenRepository,
)
from app.infrastructure.db.repositories.receipts import SqlReceiptRepository
from app.infrastructure.db.repositories.reminders import SqlReminderRepository
from app.infrastructure.db.repositories.transactions import (
    SqlLedgerQueries,
    SqlTransactionRepository,
)
from app.infrastructure.db.repositories.users import SqlUserRepository


class SqlAlchemyUnitOfWork:
    """Har `async with` yangi DB sessiyasi; commit qilinmagan o'zgarishlar bekor bo'ladi."""

    # Port tiplari bilan e'lon qilinadi: Protocol atributlari invariant, aks holda mypy
    # SqlAlchemyUnitOfWork'ni UnitOfWork sifatida qabul qilmaydi
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

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        s = self._factory()
        self._session = s
        self.users = SqlUserRepository(s)
        self.devices = SqlDeviceRepository(s)
        self.sessions = SqlSessionRepository(s)
        self.refresh_tokens = SqlRefreshTokenRepository(s)
        self.goals = SqlGoalRepository(s)
        self.transactions = SqlTransactionRepository(s)
        self.exports = SqlExportRepository(s)
        self.receipts = SqlReceiptRepository(s)
        self.reminders = SqlReminderRepository(s)
        self.accounts = SqlAccountRepository(s)
        self.categories = SqlCategoryRepository(s)
        self.ledger = SqlLedgerQueries(s)
        self.insights = SqlInsightRepository(s)
        self.faq = SqlFaqRepository(s)
        self.currency_rates = SqlCurrencyRateRepository(s)
        self.notifications = SqlNotificationRepository(s)
        self.push_tokens = SqlPushTokenRepository(s)
        self.audit = SqlAuditRepository(s)
        self.idempotency = SqlIdempotencyRepository(s)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        assert self._session is not None
        try:
            await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        assert self._session is not None
        await self._session.commit()

    async def rollback(self) -> None:
        assert self._session is not None
        await self._session.rollback()
