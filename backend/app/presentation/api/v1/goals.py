from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.application.goals.use_cases import GoalService, GoalView
from app.domain.goals.entities import EntryKind
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey
from app.presentation.schemas.goals import GoalCreateIn, GoalEntryIn, GoalOut, GoalUpdateIn

router = APIRouter(prefix="/goals", tags=["goals"])


def _svc(c: ContainerDep) -> GoalService:
    return GoalService(c.uow(), c.clock, c.settings)


def _out(v: GoalView) -> GoalOut:
    return GoalOut(id=v.id, name=v.name, target_amount=v.target_amount, saved=v.saved,
                   created_at=v.created_at)


@router.get("", response_model=list[GoalOut])
async def list_goals(ctx: AuthDep, c: ContainerDep) -> list[GoalOut]:
    return [_out(v) for v in await _svc(c).list(ctx)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GoalOut)
async def create_goal(body: GoalCreateIn, ctx: AuthDep, c: ContainerDep,
                      idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    return await _svc(c).create(ctx, body.name, body.target_amount, idempotency_key)


@router.get("/{goal_id}", response_model=GoalOut)
async def get_goal(goal_id: UUID, ctx: AuthDep, c: ContainerDep) -> GoalOut:
    return _out(await _svc(c).get(ctx, goal_id))


@router.patch("/{goal_id}", response_model=GoalOut)
async def update_goal(goal_id: UUID, body: GoalUpdateIn, ctx: AuthDep,
                      c: ContainerDep) -> GoalOut:
    return _out(await _svc(c).update(ctx, goal_id, body.name, body.target_amount))


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(goal_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await _svc(c).delete(ctx, goal_id)


@router.post("/{goal_id}/deposit", status_code=status.HTTP_201_CREATED, response_model=GoalOut)
async def deposit(goal_id: UUID, body: GoalEntryIn, ctx: AuthDep, c: ContainerDep,
                  idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    return await _svc(c).add_entry(ctx, goal_id, EntryKind.DEPOSIT, body.amount, idempotency_key)


@router.post("/{goal_id}/withdraw", status_code=status.HTTP_201_CREATED, response_model=GoalOut)
async def withdraw(goal_id: UUID, body: GoalEntryIn, ctx: AuthDep, c: ContainerDep,
                   idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    return await _svc(c).add_entry(ctx, goal_id, EntryKind.WITHDRAW, body.amount,
                                   idempotency_key)
