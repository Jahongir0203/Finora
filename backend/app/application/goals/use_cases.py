"""Goal'lar. saved faqat deposit/withdraw yozuvlaridan serverda hisoblanadi."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import Clock
from app.application.common.uow import UnitOfWork
from app.core.config import Settings
from app.domain.common.errors import NotFoundError
from app.domain.common.ids import uuid7
from app.domain.common.values import ensure_amount, ensure_name
from app.domain.goals.entities import EntryKind, Goal, GoalEntry, ensure_can_withdraw


@dataclass(frozen=True, slots=True)
class GoalView:
    id: UUID
    name: str
    target_amount: int
    saved: int
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "target_amount": self.target_amount,
            "saved": self.saved,
            "created_at": self.created_at.isoformat(),
        }


class GoalService:
    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings

    async def _view(self, uow: UnitOfWork, goal: Goal) -> GoalView:
        saved = await uow.goals.saved_amount(goal.user_id, goal.id)
        return GoalView(goal.id, goal.name, goal.target_amount, saved, goal.created_at)

    async def _get_owned(self, uow: UnitOfWork, ctx: AuthContext, goal_id: UUID,
                         *, lock: bool = False) -> Goal:
        goal = await uow.goals.get_for_user(ctx.user_id, goal_id, lock=lock)
        if goal is None:
            raise NotFoundError()
        return goal

    async def list(self, ctx: AuthContext) -> list[GoalView]:
        async with self._uow as uow:
            return [await self._view(uow, g) for g in await uow.goals.list_for_user(ctx.user_id)]

    async def get(self, ctx: AuthContext, goal_id: UUID) -> GoalView:
        async with self._uow as uow:
            return await self._view(uow, await self._get_owned(uow, ctx, goal_id))

    async def create(self, ctx: AuthContext, name: str, target_amount: int,
                     idempotency_key: str | None) -> dict[str, Any]:
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                goal = Goal(uuid7(), ctx.user_id, name, target_amount, self._clock.now())
                await uow.goals.add(goal)
                return GoalView(goal.id, goal.name, goal.target_amount, 0, goal.created_at).to_dict()

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="goal.create",
                payload={"name": name, "target_amount": target_amount},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )

    async def update(self, ctx: AuthContext, goal_id: UUID, name: str | None,
                     target_amount: int | None) -> GoalView:
        async with self._uow as uow:
            goal = await self._get_owned(uow, ctx, goal_id)
            if name is not None:
                goal.name = ensure_name(name)
            if target_amount is not None:
                goal.target_amount = ensure_amount(target_amount)
            await uow.goals.update(goal)
            view = await self._view(uow, goal)
            await uow.commit()
            return view

    async def delete(self, ctx: AuthContext, goal_id: UUID) -> None:
        async with self._uow as uow:
            if not await uow.goals.delete_for_user(ctx.user_id, goal_id):
                raise NotFoundError()
            await uow.commit()

    async def add_entry(self, ctx: AuthContext, goal_id: UUID, kind: EntryKind, amount: int,
                        idempotency_key: str | None) -> dict[str, Any]:
        ensure_amount(amount)
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                # Qatorni qulflaymiz: parallel withdraw'lar saved'dan oshib ketmasin
                goal = await self._get_owned(uow, ctx, goal_id, lock=True)
                if kind is EntryKind.WITHDRAW:
                    ensure_can_withdraw(await uow.goals.saved_amount(ctx.user_id, goal.id), amount)
                await uow.goals.add_entry(
                    GoalEntry(uuid7(), goal.id, ctx.user_id, kind, amount, self._clock.now())
                )
                return (await self._view(uow, goal)).to_dict()

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation=f"goal.{kind.value}",
                payload={"goal_id": str(goal_id), "amount": amount},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )
