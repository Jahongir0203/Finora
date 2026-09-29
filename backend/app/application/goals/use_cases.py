"""Goal'lar (BE-1101..1105). `saved` faqat deposit/withdraw yozuvlaridan serverda hisoblanadi.

Deposit hisob balansidan chiqadi, withdraw qaytadi. Goal o'chirilganda qoldiq standart hisobga
qaytariladi (bitta DB tranzaksiyasida `close` yozuvi) va goal soft delete qilinadi.
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import Clock, Notifier
from app.application.common.pagination import Page, clamp_limit, decode_cursor, encode_cursor
from app.application.common.uow import UnitOfWork
from app.application.finance.accounts import default_account, usable_account
from app.application.finance.ledger import Ledger
from app.application.notifications.triggers import goal_milestones
from app.core.config import Settings
from app.core.i18n import t
from app.domain.common.errors import NotFoundError
from app.domain.common.ids import uuid7
from app.domain.common.time import month_key, tz_or_default
from app.domain.goals.entities import (
    EntryKind,
    EntrySource,
    Goal,
    GoalEntry,
    ensure_can_withdraw,
    plan,
    progress_pct,
)
from app.domain.notifications.entities import NotificationType

logger = logging.getLogger("finora.goals")


@dataclass(frozen=True, slots=True)
class GoalView:
    goal: Goal
    saved: int
    today: date

    def to_dict(self) -> dict[str, Any]:
        g = self.goal
        p = plan(g.target_amount, self.saved, self.today, g.deadline, g.auto_save_monthly)
        return {
            "id": str(g.id), "name": g.name, "icon": g.icon, "target": g.target_amount,
            "saved": self.saved, "pct": progress_pct(self.saved, g.target_amount),
            "deadline": g.deadline.isoformat() if g.deadline else None,
            "auto_save_monthly": g.auto_save_monthly, "auto_save_day": g.auto_save_day,
            "created_at": g.created_at.isoformat(),
            "plan": {"remaining": p.remaining, "monthly_needed": p.monthly_needed,
                     "eta_months": p.eta_months},
        }


def entry_to_dict(e: GoalEntry) -> dict[str, Any]:
    return {"id": str(e.id), "kind": e.kind.value, "amount": e.amount,
            "account_id": str(e.account_id) if e.account_id else None,
            "source": e.source.value, "created_at": e.created_at.isoformat()}


@dataclass(frozen=True, slots=True)
class GoalInput:
    name: str
    target: int
    icon: str | None = None
    deadline: date | None = None
    auto_save_monthly: int | None = None
    auto_save_day: int = 1


class GoalService:
    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings, ledger: Ledger,
                 notifier: Notifier) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings
        self._ledger = ledger
        self._notifier = notifier

    def _today(self) -> date:
        return self._clock.now().date()

    async def _get_owned(self, uow: UnitOfWork, ctx: AuthContext, goal_id: UUID,
                         *, lock: bool = False) -> Goal:
        goal = await uow.goals.get_for_user(ctx.user_id, goal_id, lock=lock)
        if goal is None:
            raise NotFoundError()
        return goal

    async def list(self, ctx: AuthContext) -> list[GoalView]:
        async with self._uow as uow:
            goals = await uow.goals.list_for_user(ctx.user_id)
            saved = await uow.goals.saved_amounts(ctx.user_id)
        return [GoalView(g, saved.get(g.id, 0), self._today()) for g in goals]

    async def get(self, ctx: AuthContext, goal_id: UUID) -> GoalView:
        async with self._uow as uow:
            goal = await self._get_owned(uow, ctx, goal_id)
            return GoalView(goal, await uow.goals.saved_amount(ctx.user_id, goal.id),
                            self._today())

    async def create(self, ctx: AuthContext, data: GoalInput,
                     idempotency_key: str | None) -> dict[str, Any]:
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                now = self._clock.now()
                goal = Goal(id=uuid7(), user_id=ctx.user_id, name=data.name,
                            target_amount=data.target, created_at=now, updated_at=now,
                            icon=data.icon or "target", deadline=data.deadline,
                            auto_save_monthly=data.auto_save_monthly,
                            auto_save_day=data.auto_save_day)
                await uow.goals.add(goal)
                return GoalView(goal, 0, self._today()).to_dict()

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="goal.create",
                payload={"name": data.name, "target": data.target, "icon": data.icon,
                         "deadline": data.deadline.isoformat() if data.deadline else None,
                         "auto_save_monthly": data.auto_save_monthly,
                         "auto_save_day": data.auto_save_day},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )

    async def update(self, ctx: AuthContext, goal_id: UUID, fields: dict[str, Any]) -> GoalView:
        async with self._uow as uow:
            goal = await self._get_owned(uow, ctx, goal_id)
            mapping = {"name": "name", "target": "target_amount", "icon": "icon",
                       "deadline": "deadline", "auto_save_monthly": "auto_save_monthly",
                       "auto_save_day": "auto_save_day"}
            for key, attr in mapping.items():
                if key in fields:
                    setattr(goal, attr, fields[key])
            goal.updated_at = self._clock.now()
            goal.validate()
            await uow.goals.update(goal)
            view = GoalView(goal, await uow.goals.saved_amount(ctx.user_id, goal.id),
                            self._today())
            await uow.commit()
            return view

    async def delete(self, ctx: AuthContext, goal_id: UUID) -> int:
        """Qoldiq standart hisobga qaytadi. Javob: returned_amount."""
        async with self._uow as uow:
            goal = await self._get_owned(uow, ctx, goal_id, lock=True)
            now = self._clock.now()
            saved = await uow.goals.saved_amount(ctx.user_id, goal.id)
            # Migratsiyadan oldingi (hisobga bog'lanmagan) yozuvlar hisobdan pul olmagan —
            # hisobga faqat hisobdan kelgan qism qaytadi
            backed = await uow.goals.account_backed_amount(ctx.user_id, goal.id)
            if min(saved, backed) > 0:
                account = await default_account(uow, ctx.user_id, now)
                await uow.goals.add_entry(GoalEntry(
                    id=uuid7(), goal_id=goal.id, user_id=ctx.user_id, kind=EntryKind.WITHDRAW,
                    amount=min(saved, backed), created_at=now, account_id=account.id,
                    source=EntrySource.CLOSE))
            await uow.goals.soft_delete(ctx.user_id, goal.id, now)
            await uow.commit()
        await self._ledger.invalidate(ctx.user_id)
        return max(saved, 0)

    async def add_entry(self, ctx: AuthContext, goal_id: UUID, kind: EntryKind, amount: int,
                        account_id: UUID | None, idempotency_key: str | None) -> dict[str, Any]:
        state: dict[str, Any] = {}
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                now = self._clock.now()
                # Qatorni qulflaymiz: parallel withdraw'lar saved'dan oshib ketmasin
                goal = await self._get_owned(uow, ctx, goal_id, lock=True)
                before = await uow.goals.saved_amount(ctx.user_id, goal.id)
                if kind is EntryKind.WITHDRAW:
                    ensure_can_withdraw(before, amount)
                account = await usable_account(uow, ctx.user_id, account_id, now)
                await uow.goals.add_entry(GoalEntry(
                    id=uuid7(), goal_id=goal.id, user_id=ctx.user_id, kind=kind, amount=amount,
                    created_at=now, account_id=account.id))
                after = before + (amount if kind is EntryKind.DEPOSIT else -amount)
                state.update(goal=goal, before=before, after=after)
                return GoalView(goal, after, self._today()).to_dict()

            result = await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation=f"goal.{kind.value}",
                payload={"goal_id": str(goal_id), "amount": amount,
                         "account_id": str(account_id) if account_id else None},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )
        await self._ledger.invalidate(ctx.user_id)
        if state and kind is EntryKind.DEPOSIT:
            goal = state["goal"]
            await goal_milestones(self._notifier, ctx.user_id, goal.id, goal.name,
                                  state["before"], state["after"], goal.target_amount)
        return result

    async def history(self, ctx: AuthContext, goal_id: UUID, cursor: str | None,
                      limit: int | None) -> Page[GoalEntry]:
        size = clamp_limit(limit)
        after = decode_cursor(cursor)
        async with self._uow as uow:
            await self._get_owned(uow, ctx, goal_id)
            rows = await uow.goals.list_entries(ctx.user_id, goal_id, limit=size + 1,
                                                after=(after.at, after.id) if after else None)
        items = rows[:size]
        nxt = encode_cursor(items[-1].created_at, items[-1].id) if len(rows) > size else None
        return Page(items, nxt)


class AutoSaveJob:
    """BE-1105: har oy belgilangan kuni avtomatik deposit (idempotent: goal_id + oy).

    Hisobda mablag' yetmasa — o'tkazib yuboriladi va bildirishnoma yuboriladi.
    """

    def __init__(self, uow_factory: Any, clock: Clock, ledger: Ledger,
                 notifier: Notifier) -> None:
        self._uow = uow_factory
        self._clock = clock
        self._ledger = ledger
        self._notifier = notifier

    async def run(self) -> dict[str, int]:
        done = skipped = 0
        async with self._uow() as uow:
            goals = await uow.goals.with_auto_save()
        for goal in goals:
            try:
                result = await self._one(goal)
            except Exception:
                logger.exception("autosave_failed")
                continue
            done += result == "done"
            skipped += result == "skipped"
        return {"autosaved": done, "skipped": skipped}

    async def _one(self, goal: Goal) -> str:
        assert goal.auto_save_monthly is not None
        now = self._clock.now()
        async with self._uow() as uow:
            user = await uow.users.get(goal.user_id)
            if user is None:
                return "none"
            today = now.astimezone(tz_or_default(user.timezone)).date()
            if today.day < goal.auto_save_day:
                return "none"
            month = month_key(today)
            account = await default_account(uow, goal.user_id, now, user.language)
            balance = (await self._ledger.account_balances(uow, goal.user_id, [account],
                                                           fresh=True))[account.id]
            saved = await uow.goals.saved_amount(goal.user_id, goal.id)
            amount = min(goal.auto_save_monthly, max(goal.target_amount - saved, 0))
            if amount <= 0:
                return "none"
            if account.frozen or balance < amount:
                await uow.commit()
                skip = True
            else:
                skip = False
                added = await uow.goals.add_entry(GoalEntry(
                    id=uuid7(), goal_id=goal.id, user_id=goal.user_id, kind=EntryKind.DEPOSIT,
                    amount=amount, created_at=now, account_id=account.id,
                    source=EntrySource.AUTO, dedupe_key=f"auto:{month}"))
                await uow.commit()
                if not added:
                    return "none"
        if skip:
            await self._notifier.notify(
                goal.user_id, NotificationType.GOAL_MILESTONE,
                lambda loc: (t("notif.autosave_skipped.title", loc),
                             t("notif.autosave_skipped.body", loc, goal=goal.name)),
                dedupe_key=f"autosave_skip:{goal.id}:{month}",
            )
            return "skipped"
        await self._ledger.invalidate(goal.user_id)
        await goal_milestones(self._notifier, goal.user_id, goal.id, goal.name, saved,
                              saved + amount, goal.target_amount)
        return "done"


def plan_preview(target: int, deadline: date | None, auto_save: int | None,
                 today: date) -> dict[str, Any]:
    p = plan(target, 0, today, deadline, auto_save)
    return {"remaining": p.remaining, "monthly_needed": p.monthly_needed,
            "eta_months": p.eta_months}


