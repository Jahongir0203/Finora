from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.repositories.audit import SqlAuditRepository
from app.infrastructure.db.repositories.auth import (
    SqlDeviceRepository,
    SqlRefreshTokenRepository,
    SqlSessionRepository,
)
from app.infrastructure.db.repositories.exports import SqlExportRepository
from app.infrastructure.db.repositories.goals import SqlGoalRepository
from app.infrastructure.db.repositories.idempotency import SqlIdempotencyRepository
from app.infrastructure.db.repositories.transactions import SqlTransactionRepository
from app.infrastructure.db.repositories.users import SqlUserRepository


class SqlAlchemyUnitOfWork:
    """Har `async with` yangi DB sessiyasini ochadi; commit qilinmagan o'zgarishlar bekor bo'ladi."""

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
