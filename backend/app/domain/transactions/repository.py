from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.transactions.entities import Transaction, TransactionType


@dataclass(frozen=True, slots=True)
class TransactionFilter:
    q: str | None = None
    types: tuple[TransactionType, ...] = ()
    category_id: str | None = None
    account_id: UUID | None = None
    since: datetime | None = None
    until: datetime | None = None


class TransactionRepository(Protocol):
    """Barcha metodlar user_id talab qiladi. O'chirilganlar (deleted_at) faqat sync'da ko'rinadi."""

    async def get_for_user(self, user_id: UUID, tx_id: UUID) -> Transaction | None: ...
    async def list_for_user(
        self,
        user_id: UUID,
        flt: TransactionFilter,
        *,
        limit: int,
        after: tuple[datetime, UUID] | None = None,
        category_ids_by_name: list[str] | None = None,
    ) -> list[Transaction]:
        """occurred_at, id bo'yicha kamayish tartibida. after — cursor (keyingi sahifa).
        category_ids_by_name — `q` kategoriya nomiga mos kelgan id'lar (nom kodda/bazada)."""
        ...
    async def add(self, tx: Transaction) -> None: ...
    async def update(self, tx: Transaction) -> None: ...
    async def soft_delete(self, user_id: UUID, tx_ids: list[UUID], at: datetime) -> int: ...
    async def reassign_category(self, user_id: UUID, old: str, new: str,
                                at: datetime) -> int: ...
    async def count_for_category(self, user_id: UUID, category_id: str) -> int: ...
    async def counts_by_category(self, user_id: UUID) -> dict[str, int]: ...
    async def has_any(self, user_id: UUID) -> bool: ...
    async def changed_since(self, user_id: UUID, since: datetime,
                            limit: int) -> list[Transaction]: ...


class LedgerQueries(Protocol):
    """Agregatlar (BE-505). Hisoblash SQL'da, o'chirilgan yozuvlarsiz."""

    async def balance_deltas(self, user_id: UUID) -> dict[UUID, int]:
        """Hisob bo'yicha: kirim - chiqim ± o'tkazma - goal deposit + goal withdraw."""
        ...
    async def totals(self, user_id: UUID, since: datetime, until: datetime) -> tuple[int, int]:
        """(kirim, chiqim) — o'tkazmalarsiz."""
        ...
    async def spend_by_category(self, user_id: UUID, since: datetime,
                                until: datetime) -> dict[str, int]: ...
    async def first_transaction_at(self, user_id: UUID) -> datetime | None: ...
