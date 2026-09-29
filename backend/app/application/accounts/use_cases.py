"""Hisoblar va kartalar (BE-1401..1403), boshlang'ich balans (BE-204)."""

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import Clock
from app.application.common.uow import UnitOfWork
from app.application.finance.display import DisplayCurrency, display_currency
from app.application.finance.ledger import Ledger
from app.core.config import Settings
from app.core.i18n import t
from app.domain.accounts.entities import (
    Account,
    AccountType,
    CardNetwork,
    OnboardingLocation,
    ensure_opening_balance,
)
from app.domain.common.errors import NotFoundError
from app.domain.common.ids import uuid7
from app.domain.transactions.repository import TransactionFilter


def account_to_dict(a: Account, balance: int,
                    display: DisplayCurrency | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {
        "id": str(a.id), "type": a.type.value, "name": a.name, "bank_name": a.bank_name,
        "network": a.network.value if a.network else None, "last4": a.last4,
        "expiry": a.expiry, "color": a.color, "opening_balance": a.opening_balance,
        "monthly_limit": a.monthly_limit, "frozen": a.frozen, "is_default": a.is_default,
        "balance": balance, "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat(),
    }
    if display is not None and display.active:
        d["balance_display"] = display.amount(balance)
        d["display_currency"] = display.currency
    return d


@dataclass(frozen=True, slots=True)
class AccountInput:
    type: AccountType
    name: str | None = None
    bank_name: str | None = None
    network: CardNetwork | None = None
    last4: str | None = None
    expiry: str | None = None
    color: str | None = None
    opening_balance: int = 0
    monthly_limit: int | None = None
    is_default: bool = False


class AccountService:
    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings,
                 ledger: Ledger) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings
        self._ledger = ledger

    async def list(self, ctx: AuthContext) -> dict[str, Any]:
        async with self._uow as uow:
            accounts = await uow.accounts.list_for_user(ctx.user_id)
            balances = await self._ledger.account_balances(uow, ctx.user_id, accounts)
            user = await uow.users.get(ctx.user_id)
            display = await display_currency(uow, user.currency if user else "UZS")
        total = sum(balances.values())
        out: dict[str, Any] = {
            "total": total, "count": len(accounts),
            "items": [account_to_dict(a, balances[a.id], display) for a in accounts],
        }
        if display.active:
            out["total_display"] = display.amount(total)
            out["display_currency"] = display.currency
        return out

    async def get(self, ctx: AuthContext, account_id: UUID) -> dict[str, Any]:
        async with self._uow as uow:
            account = await uow.accounts.get_for_user(ctx.user_id, account_id)
            if account is None:
                raise NotFoundError()
            balances = await self._ledger.account_balances(uow, ctx.user_id, [account])
        return account_to_dict(account, balances[account.id])

    async def create(self, ctx: AuthContext, data: AccountInput,
                     idempotency_key: str | None) -> dict[str, Any]:
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                now = self._clock.now()
                existing = await uow.accounts.list_for_user(ctx.user_id)
                is_default = data.is_default or not existing
                if is_default:
                    await uow.accounts.clear_default(ctx.user_id)
                name = data.name or data.bank_name or t(
                    "account.cash" if data.type is AccountType.CASH else "account.card")
                account = Account(
                    id=uuid7(), user_id=ctx.user_id, type=data.type, name=name,
                    opening_balance=data.opening_balance, created_at=now, updated_at=now,
                    bank_name=data.bank_name, network=data.network, last4=data.last4,
                    expiry=data.expiry, color=data.color, monthly_limit=data.monthly_limit,
                    is_default=is_default,
                )
                await uow.accounts.add(account)
                return account_to_dict(account, account.opening_balance)

            result = await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="account.create",
                payload={k: (v.value if isinstance(v, Enum) else v)
                         for k, v in asdict(data).items()},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )
        await self._ledger.invalidate(ctx.user_id)
        return result

    async def update(self, ctx: AuthContext, account_id: UUID,
                     fields: dict[str, Any]) -> dict[str, Any]:
        async with self._uow as uow:
            account = await uow.accounts.get_for_user(ctx.user_id, account_id)
            if account is None:
                raise NotFoundError()
            for key in ("name", "bank_name", "network", "last4", "expiry", "color",
                        "opening_balance", "monthly_limit"):
                if key in fields:
                    setattr(account, key, fields[key])
            if account.name is None:
                account.name = account.bank_name or t("account.card")
            if fields.get("is_default"):
                await uow.accounts.clear_default(ctx.user_id)
                account.is_default = True
            account.updated_at = self._clock.now()
            account.validate()
            await uow.accounts.update(account)
            balances = await self._ledger.account_balances(uow, ctx.user_id, [account],
                                                           fresh=True)
            await uow.commit()
        await self._ledger.invalidate(ctx.user_id)
        return account_to_dict(account, balances[account.id])

    async def set_frozen(self, ctx: AuthContext, account_id: UUID, frozen: bool) -> None:
        async with self._uow as uow:
            account = await uow.accounts.get_for_user(ctx.user_id, account_id)
            if account is None:
                raise NotFoundError()
            account.frozen = frozen
            account.updated_at = self._clock.now()
            await uow.accounts.update(account)
            await uow.commit()

    async def delete(self, ctx: AuthContext, account_id: UUID) -> None:
        """Tranzaksiyasi bor hisob arxivlanadi (tarix saqlanadi), bo'sh hisob o'chiriladi."""
        async with self._uow as uow:
            account = await uow.accounts.get_for_user(ctx.user_id, account_id)
            if account is None:
                raise NotFoundError()
            now = self._clock.now()
            has_tx = bool(await uow.transactions.list_for_user(
                ctx.user_id, TransactionFilter(account_id=account.id), limit=1))
            if has_tx:
                account.archived_at, account.is_default, account.updated_at = now, False, now
                await uow.accounts.update(account)
            else:
                await uow.accounts.delete_for_user(ctx.user_id, account.id)
            if account.is_default or has_tx:
                rest = [a for a in await uow.accounts.list_for_user(ctx.user_id)
                        if a.id != account.id]
                if rest and not any(a.is_default for a in rest):
                    rest[0].is_default, rest[0].updated_at = True, now
                    await uow.accounts.update(rest[0])
            await uow.commit()
        await self._ledger.invalidate(ctx.user_id)


class OnboardingBalance:
    """BE-204: boshlang'ich balans hisobning `opening_balance`i sifatida (tranzaksiya emas).

    Qayta chaqirilsa shu hisob(lar) yangilanadi — dublikat yaratilmaydi.
    `both` — summa birinchi hisobga (Cash), Card 0 bilan (keyin tahrirlanadi).
    """

    def __init__(self, uow: UnitOfWork, clock: Clock, ledger: Ledger) -> None:
        self._uow = uow
        self._clock = clock
        self._ledger = ledger

    async def execute(self, ctx: AuthContext, amount: int,
                      location: OnboardingLocation) -> dict[str, Any]:
        ensure_opening_balance(amount)
        wanted = {
            OnboardingLocation.CASH: [AccountType.CASH],
            OnboardingLocation.CARD: [AccountType.CARD],
            OnboardingLocation.BOTH: [AccountType.CASH, AccountType.CARD],
        }[location]
        async with self._uow as uow:
            now = self._clock.now()
            user = await uow.users.get(ctx.user_id)
            assert user is not None
            existing = await uow.accounts.list_for_user(ctx.user_id)
            touched: list[Account] = []
            for i, acc_type in enumerate(wanted):
                opening = amount if i == 0 else 0
                account = next((a for a in existing if a.type is acc_type), None)
                if account is None:
                    key = "account.cash" if acc_type is AccountType.CASH else "account.card"
                    account = Account(
                        id=uuid7(), user_id=ctx.user_id, type=acc_type,
                        name=t(key, user.language), opening_balance=opening, created_at=now,
                        updated_at=now, is_default=not existing and i == 0,
                    )
                    await uow.accounts.add(account)
                    existing.append(account)
                elif i == 0:
                    account.opening_balance, account.updated_at = opening, now
                    await uow.accounts.update(account)
                touched.append(account)
            user.balance_set = True
            await uow.users.update(user)
            balances = await self._ledger.account_balances(uow, ctx.user_id, touched,
                                                           fresh=True)
            await uow.commit()
        await self._ledger.invalidate(ctx.user_id)
        return {"accounts": [account_to_dict(a, balances[a.id]) for a in touched]}
