from types import TracebackType
from typing import Protocol, Self

from app.application.common.idempotency import IdempotencyRepository
from app.domain.audit.repository import AuditRepository
from app.domain.auth.repository import (
    DeviceRepository,
    RefreshTokenRepository,
    SessionRepository,
)
from app.domain.exports.repository import ExportRepository
from app.domain.goals.repository import GoalRepository
from app.domain.transactions.repository import TransactionRepository
from app.domain.users.repository import UserRepository


class UnitOfWork(Protocol):
    users: UserRepository
    devices: DeviceRepository
    sessions: SessionRepository
    refresh_tokens: RefreshTokenRepository
    goals: GoalRepository
    transactions: TransactionRepository
    exports: ExportRepository
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
