from datetime import date
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.application.goals.use_cases import GoalInput, entry_to_dict, plan_preview
from app.domain.goals.entities import EntryKind
from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.goals import (
    GoalCreateIn,
    GoalDeletedOut,
    GoalEntryIn,
    GoalHistoryOut,
    GoalOut,
    GoalPlanOut,
    GoalUpdateIn,
)

router = APIRouter(prefix="/goals", tags=["goals"], responses=ERROR_RESPONSES)


@router.get("", response_model=list[GoalOut])
async def list_goals(ctx: AuthDep, c: ContainerDep) -> list[dict[str, Any]]:
    return [v.to_dict() for v in await factories.goals(c).list(ctx)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GoalOut)
async def create_goal(body: GoalCreateIn, ctx: AuthDep, c: ContainerDep,
                      idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    """`name` bo'sh — 422 goal_name_required; `target < 100 000` — 422 goal_target_min."""
    return await factories.goals(c).create(ctx, GoalInput(**body.model_dump()), idempotency_key)


@router.get("/plan", response_model=GoalPlanOut)
async def goal_plan(ctx: AuthDep, c: ContainerDep, target: Annotated[int, Query(gt=0,
                    le=10**12)], deadline: date | None = None,
                    auto_save: Annotated[int | None, Query(gt=0, le=10**12)] = None,
                    ) -> dict[str, Any]:
    """New goal sheet uchun jonli hisob (BE-1104)."""
    del ctx
    return plan_preview(target, deadline, auto_save, c.clock.now().date())


@router.get("/{goal_id}", response_model=GoalOut)
async def get_goal(goal_id: UUID, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return (await factories.goals(c).get(ctx, goal_id)).to_dict()


@router.patch("/{goal_id}", response_model=GoalOut)
async def update_goal(goal_id: UUID, body: GoalUpdateIn, ctx: AuthDep,
                      c: ContainerDep) -> dict[str, Any]:
    view = await factories.goals(c).update(ctx, goal_id, body.model_dump(exclude_unset=True))
    return view.to_dict()


@router.delete("/{goal_id}", response_model=GoalDeletedOut)
async def delete_goal(goal_id: UUID, ctx: AuthDep, c: ContainerDep) -> GoalDeletedOut:
    """`saved` asosiy hisobga qaytariladi (bitta DB tranzaksiyasida, BE-1103)."""
    return GoalDeletedOut(returned_amount=await factories.goals(c).delete(ctx, goal_id))


@router.post("/{goal_id}/deposits", status_code=status.HTTP_201_CREATED, response_model=GoalOut)
async def deposit(goal_id: UUID, body: GoalEntryIn, ctx: AuthDep, c: ContainerDep,
                  idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    return await factories.goals(c).add_entry(ctx, goal_id, EntryKind.DEPOSIT, body.amount,
                                              body.account_id, idempotency_key)


@router.post("/{goal_id}/withdrawals", status_code=status.HTTP_201_CREATED,
             response_model=GoalOut)
async def withdraw(goal_id: UUID, body: GoalEntryIn, ctx: AuthDep, c: ContainerDep,
                   idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    """`amount ≤ saved` serverda, row lock ostida tekshiriladi (422 insufficient_funds)."""
    return await factories.goals(c).add_entry(ctx, goal_id, EntryKind.WITHDRAW, body.amount,
                                              body.account_id, idempotency_key)


@router.get("/{goal_id}/history", response_model=GoalHistoryOut)
async def history(goal_id: UUID, ctx: AuthDep, c: ContainerDep,
                  cursor: Annotated[str | None, Query(max_length=200)] = None,
                  limit: Annotated[int, Query(ge=1, le=100)] = 30) -> dict[str, Any]:
    page = await factories.goals(c).history(ctx, goal_id, cursor, limit)
    return {"items": [entry_to_dict(e) for e in page.items], "next_cursor": page.next_cursor}


