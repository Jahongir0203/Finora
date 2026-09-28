from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.application.reminders.use_cases import (
    CreateReminderCommand,
    ReminderService,
    reminder_to_dict,
)
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey
from app.presentation.schemas.reminders import ReminderCreateIn, ReminderOut, ReminderUpdateIn

router = APIRouter(prefix="/reminders", tags=["reminders"])


def _svc(c: ContainerDep) -> ReminderService:
    return ReminderService(c.uow(), c.clock, c.settings)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReminderOut)
async def create_reminder(body: ReminderCreateIn, ctx: AuthDep, c: ContainerDep,
                          idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    cmd = CreateReminderCommand(title=body.title, due_at=body.due_at, repeat=body.repeat,
                                amount=body.amount)
    return await _svc(c).create(ctx, cmd, idempotency_key)


@router.get("", response_model=list[ReminderOut])
async def list_reminders(ctx: AuthDep, c: ContainerDep) -> list[dict[str, Any]]:
    return [reminder_to_dict(r) for r in await _svc(c).list(ctx)]


@router.get("/{reminder_id}", response_model=ReminderOut)
async def get_reminder(reminder_id: UUID, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return reminder_to_dict(await _svc(c).get(ctx, reminder_id))


@router.patch("/{reminder_id}", response_model=ReminderOut)
async def update_reminder(reminder_id: UUID, body: ReminderUpdateIn, ctx: AuthDep,
                          c: ContainerDep) -> dict[str, Any]:
    # Faqat yuborilgan maydonlar o'zgaradi; "amount": null — summani olib tashlaydi
    fields = body.model_dump(exclude_unset=True)
    reminder = await _svc(c).update(ctx, reminder_id, **fields)
    return reminder_to_dict(reminder)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(reminder_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await _svc(c).delete(ctx, reminder_id)
