import base64
import binascii

from fastapi import APIRouter, Depends, Request, status

from app.application.auth.dto import (
    PinFailuresCommand,
    RefreshCommand,
    RequestOtpCommand,
    VerifyOtpCommand,
)
from app.application.auth.otp import RequestOtp, VerifyOtp
from app.application.auth.sessions import Logout, LogoutAll, RefreshTokens, ReportPinFailures
from app.application.auth.tokens import TokenIssuer
from app.domain.common.errors import ValidationFailedError
from app.presentation.api.deps import (
    AuthDep,
    ContainerDep,
    DeviceProofDep,
    client_ip,
    token_issuer,
)
from app.presentation.schemas.auth import (
    OtpRequestIn,
    OtpVerifyIn,
    RefreshIn,
    TokenOut,
    VerifyOut,
)
from app.presentation.schemas.common import MessageOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _decode_key(value: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(value.replace("+", "-").replace("/", "_")
                                        + "=" * (-len(value) % 4))
    except (binascii.Error, ValueError):
        raise ValidationFailedError("Qurilma kaliti noto'g'ri") from None


@router.post("/otp", status_code=status.HTTP_202_ACCEPTED, response_model=MessageOut)
async def request_otp(body: OtpRequestIn, request: Request, c: ContainerDep) -> MessageOut:
    await RequestOtp(c.kv, c.limiter, c.hasher, c.sms, c.clock, c.settings).execute(
        RequestOtpCommand(phone=body.phone, ip=client_ip(request),
                          installation_id=body.installation_id)
    )
    # Raqam ro'yxatdan o'tgan-o'tmaganidan qat'i nazar bir xil javob
    return MessageOut(message="Kod yuborildi")


@router.post("/verify", response_model=VerifyOut)
async def verify_otp(body: OtpVerifyIn, request: Request, c: ContainerDep,
                     tokens: TokenIssuer = Depends(token_issuer)) -> VerifyOut:
    result = await VerifyOtp(
        c.uow(), c.kv, c.limiter, c.hasher, c.cipher, c.key_verifier, tokens,
        c.notifier, c.clock, c.settings,
    ).execute(VerifyOtpCommand(
        phone=body.phone, code=body.code, ip=client_ip(request),
        installation_id=body.installation_id,
        device_public_key=_decode_key(body.device_public_key),
        device_name=body.device_name, platform=body.platform, pin_reset=body.pin_reset,
    ))
    t = result.tokens
    return VerifyOut(access_token=t.access_token, refresh_token=t.refresh_token,
                     expires_in=t.expires_in, is_new_user=result.is_new_user)


@router.post("/refresh", response_model=TokenOut)
async def refresh(body: RefreshIn, proof: DeviceProofDep, c: ContainerDep,
                  tokens: TokenIssuer = Depends(token_issuer)) -> TokenOut:
    pair = await RefreshTokens(
        c.uow(), c.hasher, c.key_verifier, tokens, c.limiter, c.notifier, c.clock, c.settings,
    ).execute(RefreshCommand(refresh_token=body.refresh_token, proof=proof))
    return TokenOut(access_token=pair.access_token, refresh_token=pair.refresh_token,
                    expires_in=pair.expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(ctx: AuthDep, c: ContainerDep) -> None:
    await Logout(c.uow(), c.clock).execute(ctx)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(ctx: AuthDep, c: ContainerDep) -> None:
    await LogoutAll(c.uow(), c.clock).execute(ctx)


@router.post("/pin-failures", status_code=status.HTTP_204_NO_CONTENT)
async def pin_failures(body: RefreshIn, proof: DeviceProofDep, request: Request,
                       c: ContainerDep) -> None:
    await ReportPinFailures(c.uow(), c.hasher, c.key_verifier, c.notifier, c.clock,
                            c.settings).execute(
        PinFailuresCommand(refresh_token=body.refresh_token, proof=proof, ip=client_ip(request))
    )
