from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.transactions.entities import Transaction


class TransactionRepository(Protocol):
    async def get_for_user(self, user_id: UUID, tx_id: UUID) -> Transaction | None: ...
    async def list_for_user(
        self,
        user_id: UUID,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 50,
        before_id: UUID | None = None,
    ) -> list[Transaction]: ...
    async def add(self, tx: Transaction) -> None: ...
    async def delete_for_user(self, user_id: UUID, tx_id: UUID) -> bool: ...
    async def totals_by_category(
        self, user_id: UUID, since: datetime, until: datetime
    ) -> dict[str, int]: ...
