"""Standart hisob: account_id berilmagan tranzaksiya va goal yozuvlari shu hisobga tushadi."""

from datetime import datetime
from uuid import UUID

from app.application.common.uow import UnitOfWork
from app.core.i18n import t
from app.domain.accounts.entities import Account, AccountType
from app.domain.common.errors import AccountFrozenError, ValidationFailedError
from app.domain.common.ids import uuid7


async def default_account(uow: UnitOfWork, user_id: UUID, now: datetime,
                          locale: str | None = None) -> Account:
    """Hisob bo'lmasa — "Cash" (0 so'm) yaratiladi, shunda tranzaksiya doim hisobga bog'lanadi."""
    account = await uow.accounts.get_default(user_id)
    if account is not None:
        return account
    account = Account(id=uuid7(), user_id=user_id, type=AccountType.CASH,
                      name=t("account.cash", locale), opening_balance=0, created_at=now,
                      updated_at=now, is_default=True)
    await uow.accounts.add(account)
    return account


async def usable_account(uow: UnitOfWork, user_id: UUID, account_id: UUID | None,
                         now: datetime, locale: str | None = None) -> Account:
    """Tanlangan (yoki standart) hisob; muzlatilgan bo'lsa — 422 account_frozen (BE-1403)."""
    if account_id is None:
        account = await default_account(uow, user_id, now, locale)
    else:
        found = await uow.accounts.get_for_user(user_id, account_id)
        if found is None:
            raise ValidationFailedError("Hisob topilmadi", fields=["account_id"])
        account = found
    if account.frozen:
        raise AccountFrozenError()
    return account
