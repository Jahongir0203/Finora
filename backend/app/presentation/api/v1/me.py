from uuid import UUID

from fastapi import APIRouter, status

from app.application.account.use_cases import DeleteAccount
from app.application.auth.sessions import ListDevices, SignOutDevice
from app.presentation.api.deps import AuthDep, ContainerDep
from app.presentation.schemas.auth import DeviceOut

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
