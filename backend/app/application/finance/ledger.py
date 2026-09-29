"""Hisob-kitob servisi (BE-505): balans, oylik kirim/chiqim, kategoriya xarajati.

Barcha endpointlar (Home, Accounts, Stats, Budgets, Insights) shu yerdan foydalanadi —
bir xil formula bir joyda:
    hisob balansi = opening_balance + kirim - chiqim ± o'tkazma - goal deposit + goal withdraw
"""

from datetime import datetime, tzinfo
from uuid import UUID

from app.application.common.uow import UnitOfWork
from app.application.finance.cache import AggregateCache
from app.domain.accounts.entities import Account
from app.domain.common.time import month_bounds


class Ledger:
    def __init__(self, cache: AggregateCache) -> None:
        self._cache = cache

    async def account_balances(self, uow: UnitOfWork, user_id: UUID,
                               accounts: list[Account] | None = None, *,
                               fresh: bool = False) -> dict[UUID, int]:
        """Arxivlanmagan hisoblar balansi.

        fresh=True — keshni o'qimaydi va yozmaydi: hali commit bo'lmagan tranzaksiya ichida
        (javobga yangi balans qo'shish uchun) kesh ifloslanmasin.
        """
        if accounts is None:
            accounts = await uow.accounts.list_for_user(user_id)
        cached = None if fresh else await self._cache.get(user_id, "deltas")
        if cached is None:
            deltas = await uow.ledger.balance_deltas(user_id)
            if not fresh:
                await self._cache.set(user_id, "deltas",
                                      {str(k): v for k, v in deltas.items()})
        else:
            deltas = {UUID(k): int(v) for k, v in cached.items()}
        return {a.id: a.opening_balance + deltas.get(a.id, 0) for a in accounts}

    async def total_balance(self, uow: UnitOfWork, user_id: UUID, *, fresh: bool = False) -> int:
        return sum((await self.account_balances(uow, user_id, fresh=fresh)).values())

    async def month_totals(self, uow: UnitOfWork, user_id: UUID, now: datetime,
                           tz: tzinfo) -> tuple[int, int]:
        """(kirim, chiqim) joriy oy uchun, foydalanuvchi vaqt zonasida."""
        since, until = month_bounds(now, tz)
        name = f"month:{since.isoformat()}"
        cached = await self._cache.get(user_id, name)
        if cached is not None:
            return int(cached[0]), int(cached[1])
        income, expense = await uow.ledger.totals(user_id, since, until)
        await self._cache.set(user_id, name, [income, expense])
        return income, expense

    async def month_spend_by_category(self, uow: UnitOfWork, user_id: UUID, now: datetime,
                                      tz: tzinfo) -> dict[str, int]:
        since, until = month_bounds(now, tz)
        name = f"cat:{since.isoformat()}"
        cached = await self._cache.get(user_id, name)
        if cached is not None:
            return {k: int(v) for k, v in cached.items()}
        spend = await uow.ledger.spend_by_category(user_id, since, until)
        await self._cache.set(user_id, name, spend)
        return spend

    async def invalidate(self, user_id: UUID) -> None:
        await self._cache.invalidate(user_id)
