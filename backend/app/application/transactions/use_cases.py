"""Tranzaksiyalar (BE-501..504) va o'tkazmalar (BE-1404)."""

import dataclasses
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta, tzinfo
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import Clock, Notifier
from app.application.common.pagination import Page, clamp_limit, decode_cursor, encode_cursor
from app.application.common.uow import UnitOfWork
from app.application.finance.accounts import usable_account
from app.application.finance.catalog import CategoryCatalog
from app.application.finance.display import DisplayCurrency, display_currency
from app.application.finance.ledger import Ledger
from app.application.notifications.triggers import check_budget
from app.core.config import Settings
from app.domain.categories.entities import TRANSFER_CATEGORY_ID
from app.domain.common.errors import NotFoundError, ValidationFailedError
from app.domain.common.ids import uuid7
from app.domain.common.time import day_bounds
from app.domain.transactions.entities import (
    Transaction,
    TransactionSource,
    TransactionType,
    TransferDirection,
)
from app.domain.transactions.repository import TransactionFilter

# Kelajakdagi sana: mijoz soati biroz oldinda bo'lishi mumkin, lekin "ertangi" yozuv emas
MAX_FUTURE = timedelta(days=1)
GROUPS_SCAN_LIMIT = 5000


def transaction_to_dict(tx: Transaction, display: DisplayCurrency | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {
        "id": str(tx.id),
        "type": tx.type.value,
        "amount": tx.amount,
        "currency": tx.currency,
        "category_id": tx.category_id,
        "account_id": str(tx.account_id),
        "title": tx.title,
        "note": tx.note,
        "source": tx.source.value,
        "receipt_id": str(tx.receipt_id) if tx.receipt_id else None,
        # API'da vaqt har doim UTC (mijoz yuborgan +05:00 ham)
        "occurred_at": tx.occurred_at.astimezone(UTC).isoformat(),
        "created_at": tx.created_at.isoformat(),
        "updated_at": tx.updated_at.isoformat(),
        "transfer_peer_id": str(tx.transfer_peer_id) if tx.transfer_peer_id else None,
        "direction": tx.direction.value if tx.direction else None,
    }
    if display is not None and display.active:
        d["amount_display"] = display.amount(tx.amount)
        d["display_currency"] = display.currency
    return d


@dataclass(frozen=True, slots=True)
class CreateTransactionCommand:
    type: TransactionType
    amount: int
    category_id: str
    title: str | None = None
    note: str | None = None
    account_id: UUID | None = None
    occurred_at: datetime | None = None
    source: TransactionSource = TransactionSource.MANUAL
    receipt_id: UUID | None = None
    client_created_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UpdateTransactionCommand:
    amount: int | None = None
    category_id: str | None = None
    title: str | None = None
    note: str | None = None
    account_id: UUID | None = None
    occurred_at: datetime | None = None
    # Qaysi maydonlar yuborilgan (None qiymat bilan tozalash uchun: title, note)
    fields: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class DayGroup:
    date: date
    net: int


@dataclass(frozen=True, slots=True)
class TransactionPage:
    page: Page[Transaction]
    groups: list[DayGroup]


async def _day_groups(uow: UnitOfWork, user_id: UUID, flt: TransactionFilter,
                     items: list[Transaction], name_ids: list[str] | None,
                     tz: tzinfo) -> list[DayGroup]:
    """Sahifadagi kunlar uchun to'liq kunlik net (shu filtr bo'yicha, sahifadan tashqari ham)."""
    if not items:
        return []
    dates = sorted({t.occurred_at.astimezone(tz).date() for t in items}, reverse=True)
    since, _ = day_bounds(dates[-1], tz)
    _, until = day_bounds(dates[0], tz)
    span = dataclasses.replace(
        flt, since=max(since, flt.since) if flt.since else since,
        until=min(until, flt.until) if flt.until else until,
    )
    rows = await uow.transactions.list_for_user(user_id, span, limit=GROUPS_SCAN_LIMIT,
                                                category_ids_by_name=name_ids)
    net: dict[date, int] = dict.fromkeys(dates, 0)
    for r in rows:
        d = r.occurred_at.astimezone(tz).date()
        if d in net:
            net[d] += r.signed_amount
    return [DayGroup(d, net[d]) for d in dates]


class TransactionService:
    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings, ledger: Ledger,
                 notifier: Notifier) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings
        self._ledger = ledger
        self._notifier = notifier

    def _check_time(self, at: datetime | None) -> datetime:
        now = self._clock.now()
        if at is None:
            return now
        if at > now + MAX_FUTURE:
            raise ValidationFailedError("Sana kelajakda", fields=["occurred_at"])
        return at

    async def create(self, ctx: AuthContext, cmd: CreateTransactionCommand,
                     idempotency_key: str | None, tz: tzinfo) -> dict[str, Any]:
        if cmd.type is TransactionType.TRANSFER:
            raise ValidationFailedError("O'tkazma uchun /v1/transfers", fields=["type"])
        occurred_at = self._check_time(cmd.occurred_at)
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                now = self._clock.now()
                catalog = await CategoryCatalog.load(uow, ctx.user_id)
                catalog.require(cmd.category_id, cmd.type)
                account = await usable_account(uow, ctx.user_id, cmd.account_id, now)
                source = cmd.source
                if cmd.receipt_id is not None:
                    receipt = await uow.receipts.get_for_user(ctx.user_id, cmd.receipt_id)
                    if receipt is None:
                        raise ValidationFailedError("Chek topilmadi", fields=["receipt_id"])
                    await uow.receipts.confirm(ctx.user_id, receipt.id, now)
                    source = TransactionSource.SCAN
                tx = Transaction(
                    id=uuid7(), user_id=ctx.user_id, account_id=account.id, type=cmd.type,
                    amount=cmd.amount, category_id=cmd.category_id, occurred_at=occurred_at,
                    created_at=now, updated_at=now, title=cmd.title, note=cmd.note,
                    source=source, receipt_id=cmd.receipt_id,
                    client_created_at=cmd.client_created_at,
                )
                await uow.transactions.add(tx)
                total = await self._ledger.total_balance(uow, ctx.user_id, fresh=True)
                return {"transaction": transaction_to_dict(tx), "balance": {"total": total}}

            result = await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="transaction.create",
                payload={
                    "type": cmd.type.value, "amount": cmd.amount, "category_id": cmd.category_id,
                    "title": cmd.title, "note": cmd.note,
                    "account_id": str(cmd.account_id) if cmd.account_id else None,
                    "occurred_at": cmd.occurred_at.isoformat() if cmd.occurred_at else None,
                    "receipt_id": str(cmd.receipt_id) if cmd.receipt_id else None,
                },
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )
        await self._ledger.invalidate(ctx.user_id)
        if cmd.type is TransactionType.EXPENSE:
            async with self._uow as uow:
                await check_budget(uow, self._ledger, self._notifier, ctx.user_id,
                                   cmd.category_id, self._clock.now(), tz)
        return result

    async def get(self, ctx: AuthContext, tx_id: UUID) -> tuple[Transaction, DisplayCurrency]:
        async with self._uow as uow:
            tx = await uow.transactions.get_for_user(ctx.user_id, tx_id)
            if tx is None:
                raise NotFoundError()
            user = await uow.users.get(ctx.user_id)
            display = await display_currency(uow, user.currency if user else "UZS")
        return tx, display

    async def list(self, ctx: AuthContext, flt: TransactionFilter, *, cursor: str | None,
                   limit: int | None, tz: tzinfo) -> tuple[TransactionPage, DisplayCurrency]:
        size = clamp_limit(limit)
        after = decode_cursor(cursor)
        async with self._uow as uow:
            name_ids = None
            if flt.q:
                name_ids = (await CategoryCatalog.load(uow, ctx.user_id)).ids_matching(flt.q)
            rows = await uow.transactions.list_for_user(
                ctx.user_id, flt, limit=size + 1,
                after=(after.at, after.id) if after else None, category_ids_by_name=name_ids,
            )
            items = rows[:size]
            next_cursor = (encode_cursor(items[-1].occurred_at, items[-1].id)
                           if len(rows) > size else None)
            groups = await _day_groups(uow, ctx.user_id, flt, items, name_ids, tz)
            user = await uow.users.get(ctx.user_id)
            display = await display_currency(uow, user.currency if user else "UZS")
        return TransactionPage(Page(items, next_cursor), groups), display

    async def update(self, ctx: AuthContext, tx_id: UUID,
                     cmd: UpdateTransactionCommand) -> Transaction:
        async with self._uow as uow:
            tx = await uow.transactions.get_for_user(ctx.user_id, tx_id)
            if tx is None:
                raise NotFoundError()
            now = self._clock.now()
            if tx.type is TransactionType.TRANSFER:
                if cmd.fields & {"category_id", "account_id"}:
                    raise ValidationFailedError("O'tkazmada hisob/kategoriya o'zgarmaydi",
                                                fields=sorted(cmd.fields & {"category_id",
                                                                            "account_id"}))
            if "amount" in cmd.fields and cmd.amount is not None:
                tx.amount = cmd.amount
            if "category_id" in cmd.fields and cmd.category_id is not None:
                (await CategoryCatalog.load(uow, ctx.user_id)).require(cmd.category_id, tx.type)
                tx.category_id = cmd.category_id
            if "account_id" in cmd.fields and cmd.account_id is not None:
                tx.account_id = (await usable_account(uow, ctx.user_id, cmd.account_id, now)).id
            if "title" in cmd.fields:
                tx.title = cmd.title
            if "note" in cmd.fields:
                tx.note = cmd.note
            if "occurred_at" in cmd.fields and cmd.occurred_at is not None:
                tx.occurred_at = self._check_time(cmd.occurred_at)
            tx.updated_at = now
            tx.validate()
            await uow.transactions.update(tx)
            if tx.transfer_peer_id is not None:
                peer = await uow.transactions.get_for_user(ctx.user_id, tx.transfer_peer_id)
                if peer is not None:
                    peer.amount, peer.occurred_at, peer.note = tx.amount, tx.occurred_at, tx.note
                    peer.title, peer.updated_at = tx.title, now
                    await uow.transactions.update(peer)
            await uow.commit()
        await self._ledger.invalidate(ctx.user_id)
        return tx

    async def delete(self, ctx: AuthContext, tx_id: UUID) -> None:
        async with self._uow as uow:
            tx = await uow.transactions.get_for_user(ctx.user_id, tx_id)
            if tx is None:
                raise NotFoundError()
            ids = [tx.id] + ([tx.transfer_peer_id] if tx.transfer_peer_id else [])
            await uow.transactions.soft_delete(ctx.user_id, ids, self._clock.now())
            await uow.commit()
        await self._ledger.invalidate(ctx.user_id)


class TransferService:
    """Ikki bog'langan yozuv: from hisobdan `out`, to hisobga `in` (statistikada xarajat emas)."""

    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings,
                 ledger: Ledger) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings
        self._ledger = ledger

    async def create(self, ctx: AuthContext, from_account_id: UUID, to_account_id: UUID,
                     amount: int, note: str | None, occurred_at: datetime | None,
                     idempotency_key: str | None) -> dict[str, Any]:
        if from_account_id == to_account_id:
            raise ValidationFailedError("Hisoblar bir xil", fields=["to_account_id"])
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                now = self._clock.now()
                src = await usable_account(uow, ctx.user_id, from_account_id, now)
                dst = await usable_account(uow, ctx.user_id, to_account_id, now)
                at = occurred_at or now
                out_id, in_id = uuid7(), uuid7()
                common: dict[str, Any] = {
                    "user_id": ctx.user_id, "type": TransactionType.TRANSFER,
                    "amount": amount, "category_id": TRANSFER_CATEGORY_ID, "occurred_at": at,
                    "created_at": now, "updated_at": now, "note": note,
                }
                out = Transaction(id=out_id, account_id=src.id, transfer_peer_id=in_id,
                                  direction=TransferDirection.OUT, **common)
                inc = Transaction(id=in_id, account_id=dst.id, transfer_peer_id=out_id,
                                  direction=TransferDirection.IN, **common)
                await uow.transactions.add(out)
                await uow.transactions.add(inc)
                return {"out": transaction_to_dict(out), "in": transaction_to_dict(inc)}

            result = await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="transfer.create",
                payload={"from": str(from_account_id), "to": str(to_account_id),
                         "amount": amount, "note": note,
                         "occurred_at": occurred_at.isoformat() if occurred_at else None},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )
        await self._ledger.invalidate(ctx.user_id)
        return result
