from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.accounts.entities import Account, AccountType, CardNetwork
from app.infrastructure.db.models import AccountModel


def _account(m: AccountModel) -> Account:
    return Account(
        id=m.id, user_id=m.user_id, type=AccountType(m.type), name=m.name,
        opening_balance=m.opening_balance, created_at=m.created_at, updated_at=m.updated_at,
        bank_name=m.bank_name, network=CardNetwork(m.network) if m.network else None,
        last4=m.last4, expiry=m.expiry, color=m.color, monthly_limit=m.monthly_limit,
        frozen=m.frozen, is_default=m.is_default, archived_at=m.archived_at,
    )


def _values(a: Account) -> dict[str, object]:
    return {
        "type": a.type.value, "name": a.name, "bank_name": a.bank_name,
        "network": a.network.value if a.network else None, "last4": a.last4,
        "expiry": a.expiry, "color": a.color, "opening_balance": a.opening_balance,
        "monthly_limit": a.monthly_limit, "frozen": a.frozen, "is_default": a.is_default,
        "updated_at": a.updated_at, "archived_at": a.archived_at,
    }


class SqlAccountRepository:
    """Har bir so'rov `WHERE id = :id AND user_id = :sub`."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, account: Account) -> None:
        self._s.add(AccountModel(id=account.id, user_id=account.user_id,
                                 created_at=account.created_at, **_values(account)))
        await self._s.flush()

    async def get_for_user(self, user_id: UUID, account_id: UUID, *,
                           include_archived: bool = False) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.id == account_id,
                                          AccountModel.user_id == user_id)
        if not include_archived:
            stmt = stmt.where(AccountModel.archived_at.is_(None))
        m = await self._s.scalar(stmt)
        return _account(m) if m else None

    async def list_for_user(self, user_id: UUID, *,
                            include_archived: bool = False) -> list[Account]:
        stmt = select(AccountModel).where(AccountModel.user_id == user_id)
        if not include_archived:
            stmt = stmt.where(AccountModel.archived_at.is_(None))
        stmt = stmt.order_by(AccountModel.is_default.desc(), AccountModel.id)
        return [_account(m) for m in await self._s.scalars(stmt)]

    async def get_default(self, user_id: UUID) -> Account | None:
        m = await self._s.scalar(
            select(AccountModel).where(AccountModel.user_id == user_id,
                                       AccountModel.archived_at.is_(None))
            .order_by(AccountModel.is_default.desc(), AccountModel.id).limit(1)
        )
        return _account(m) if m else None

    async def update(self, account: Account) -> None:
        await self._s.execute(
            update(AccountModel)
            .where(AccountModel.id == account.id, AccountModel.user_id == account.user_id)
            .values(**_values(account))
        )

    async def clear_default(self, user_id: UUID) -> None:
        await self._s.execute(
            update(AccountModel).where(AccountModel.user_id == user_id,
                                       AccountModel.is_default.is_(True))
            .values(is_default=False)
        )

    async def delete_for_user(self, user_id: UUID, account_id: UUID) -> bool:
        result = await self._s.execute(
            delete(AccountModel).where(AccountModel.id == account_id,
                                       AccountModel.user_id == user_id)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def changed_since(self, user_id: UUID, since: datetime, limit: int) -> list[Account]:
        rows = await self._s.scalars(
            select(AccountModel).where(AccountModel.user_id == user_id,
                                       AccountModel.updated_at > since)
            .order_by(AccountModel.updated_at).limit(limit)
        )
        return [_account(m) for m in rows]
