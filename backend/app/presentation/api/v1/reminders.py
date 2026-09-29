from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.application.reminders.use_cases import CreateReminderCommand, reminder_to_dict
from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey, TzDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.reminders import (
    ReminderCreateIn,
    ReminderOut,
    ReminderPaidOut,
    ReminderPayIn,
    ReminderUpdateIn,
)

router = APIRouter(prefix="/reminders", tags=["reminders"], responses=ERROR_RESPONSES)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReminderOut)
async def create_reminder(body: ReminderCreateIn, ctx: AuthDep, c: ContainerDep, tz: TzDep,
                          idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    cmd = CreateReminderCommand(title=body.title, category_id=body.category_id,
                                amount=body.amount, due_date=body.due_date, repeat=body.repeat)
    return await factories.reminders(c).create(ctx, cmd, idempotency_key, tz)


@router.get("", response_model=list[ReminderOut])
async def list_reminders(ctx: AuthDep, c: ContainerDep, tz: TzDep) -> list[dict[str, Any]]:
    svc = factories.reminders(c)
    today = svc.today(tz)
    return [reminder_to_dict(r, today) for r in await svc.list(ctx, tz)]


@router.get("/{reminder_id}", response_model=ReminderOut)
async def get_reminder(reminder_id: UUID, ctx: AuthDep, c: ContainerDep,
                       tz: TzDep) -> dict[str, Any]:
    svc = factories.reminders(c)
    return reminder_to_dict(await svc.get(ctx, reminder_id), svc.today(tz))


@router.patch("/{reminder_id}", response_model=ReminderOut)
async def update_reminder(reminder_id: UUID, body: ReminderUpdateIn, ctx: AuthDep,
                          c: ContainerDep, tz: TzDep) -> dict[str, Any]:
    """Switch: `{ "enabled": false }`."""
    svc = factories.reminders(c)
    fields = body.model_dump(exclude_unset=True, exclude_none=True)
    return reminder_to_dict(await svc.update(ctx, reminder_id, fields), svc.today(tz))


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(reminder_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await factories.reminders(c).delete(ctx, reminder_id)


@router.post("/{reminder_id}/pay", status_code=status.HTTP_201_CREATED,
             response_model=ReminderPaidOut)
async def pay_reminder(reminder_id: UUID, ctx: AuthDep, c: ContainerDep, tz: TzDep,
                       body: ReminderPayIn | None = None,
                       idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    """Chiqim tranzaksiyasi yaratadi va keyingi sanaga suradi (BE-1203)."""
    return await factories.reminders(c).pay(ctx, reminder_id, body.account_id if body else None,
                                            idempotency_key, tz)
