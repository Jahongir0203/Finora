from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.application.account.use_cases import DeleteAccount
from app.application.auth.sessions import ListDevices, SignOutDevice
from app.application.notifications.use_cases import NotificationService
from app.presentation.api.deps import AuthDep, ContainerDep
from app.presentation.schemas.auth import DeviceOut
from app.presentation.schemas.notifications import NotificationOut, PushTokenIn

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/devices", response_model=list[DeviceOut])
async def list_devices(ctx: AuthDep, c: ContainerDep) -> list[DeviceOut]:
    devices = await ListDevices(c.uow()).execute(ctx)
    return [DeviceOut(id=d.id, name=d.name, platform=d.platform, created_at=d.created_at,
                      last_seen_at=d.last_seen_at, is_current=d.is_current) for d in devices]


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def sign_out_device(device_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await SignOutDevice(c.uow(), c.clock).execute(ctx, device_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(ctx: AuthDep, c: ContainerDep) -> None:
    await DeleteAccount(c.uow(), c.storage, c.clock).execute(ctx)


@router.put("/push-token", status_code=status.HTTP_204_NO_CONTENT)
async def register_push_token(body: PushTokenIn, ctx: AuthDep, c: ContainerDep) -> None:
    await NotificationService(c.uow(), c.clock).register_push_token(ctx, body.provider, body.token)


@router.delete("/push-token", status_code=status.HTTP_204_NO_CONTENT)
async def remove_push_token(ctx: AuthDep, c: ContainerDep) -> None:
    await NotificationService(c.uow(), c.clock).remove_push_token(ctx)


@router.get("/notifications", response_model=list[NotificationOut])
async def list_notifications(
    ctx: AuthDep, c: ContainerDep, limit: Annotated[int, Query(ge=1, le=100)] = 50
) -> list[NotificationOut]:
    items = await NotificationService(c.uow(), c.clock).list(ctx, limit)
    return [NotificationOut(id=n.id, kind=n.kind, title=n.title, body=n.body,
                            created_at=n.created_at, read_at=n.read_at) for n in items]


@router.post("/notifications/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(notification_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await NotificationService(c.uow(), c.clock).mark_read(ctx, notification_id)
