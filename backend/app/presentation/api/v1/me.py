from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request, status

from app.application.account.use_cases import DeleteAccount, SendDeletionCode
from app.application.auth.sessions import SignOutDevice
from app.application.profile.use_cases import DeviceService, ProfileService
from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, TimezoneHeader, client_ip
from app.presentation.schemas.auth import DeviceOut, OtpSentOut
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.notifications import CountOut
from app.presentation.schemas.profile import (
    DeleteAccountIn,
    DeviceSettingsOut,
    MeOut,
    PinSetupIn,
    ProfileUpdateIn,
    SettingsIn,
)

router = APIRouter(prefix="/me", tags=["profile"], responses=ERROR_RESPONSES)


def _profile(c: ContainerDep) -> ProfileService:
    return ProfileService(c.uow(), c.clock, c.cipher)


@router.get("", response_model=MeOut)
async def get_me(ctx: AuthDep, c: ContainerDep,
                 x_timezone: TimezoneHeader = None) -> dict[str, Any]:
    return await _profile(c).me(ctx, x_timezone)


@router.patch("", response_model=MeOut)
async def update_me(body: ProfileUpdateIn, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return await _profile(c).update_name(ctx, body.model_dump(exclude_unset=True))


@router.patch("/settings", response_model=MeOut)
async def update_settings(body: SettingsIn, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    fields = {k: v.value if hasattr(v, "value") else v
              for k, v in body.model_dump(exclude_unset=True, exclude_none=True).items()}
    return await _profile(c).update_settings(ctx, fields)


@router.post("/pin-setup", response_model=DeviceSettingsOut)
async def pin_setup(body: PinSetupIn, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return await _profile(c).pin_setup(ctx, body.device_id)


@router.get("/devices", response_model=list[DeviceOut])
async def list_devices(ctx: AuthDep, c: ContainerDep) -> list[dict[str, Any]]:
    return await DeviceService(c.uow(), c.clock, c.notifier).list(ctx)


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def sign_out_device(device_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await SignOutDevice(c.uow(), c.clock).execute(ctx, device_id)


@router.post("/devices/logout-all", response_model=CountOut)
async def logout_other_devices(ctx: AuthDep, c: ContainerDep) -> CountOut:
    """Joriy qurilmadan tashqari barcha sessiyalar bekor qilinadi (BE-1303)."""
    n = await DeviceService(c.uow(), c.clock, c.notifier).logout_others(ctx)
    return CountOut(count=n)


@router.post("/delete-code", response_model=OtpSentOut)
async def send_deletion_code(ctx: AuthDep, c: ContainerDep, request: Request) -> OtpSentOut:
    """Akkauntni o'chirishdan oldin SMS kod (BE-1304)."""
    sent = await SendDeletionCode(c.uow(), c.cipher, factories.request_otp(c)).execute(
        ctx, client_ip(request))
    return OtpSentOut(resend_after=sent.resend_after, expires_in=sent.expires_in)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(body: DeleteAccountIn, ctx: AuthDep, c: ContainerDep) -> None:
    await DeleteAccount(c.uow(), c.storage, c.clock, factories.otp_checker(c)).execute(
        ctx, body.code)
