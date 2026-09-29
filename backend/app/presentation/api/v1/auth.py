import base64
import binascii

from fastapi import APIRouter, Request, status

from app.application.auth.dto import RefreshCommand, RequestOtpCommand, VerifyOtpCommand
from app.application.auth.otp import VerifyOtp
from app.application.auth.sessions import Logout, RefreshTokens
from app.domain.common.errors import ValidationFailedError
from app.presentation.api import factories
from app.presentation.api.deps import (
    AuthDep,
    ContainerDep,
    DeviceProofDep,
    TokenIssuerDep,
    client_ip,
)
from app.presentation.schemas.auth import (
    OnboardingOut,
    OtpPurpose,
    OtpRequestIn,
    OtpSentOut,
    OtpVerifyIn,
    RefreshIn,
    TokenOut,
    VerifyOut,
    VerifyUserOut,
)
from app.presentation.schemas.common import ERROR_RESPONSES

router = APIRouter(prefix="/auth", tags=["auth"], responses=ERROR_RESPONSES)


def _decode_key(value: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(value.replace("+", "-").replace("/", "_")
                                        + "=" * (-len(value) % 4))
    except (binascii.Error, ValueError):
        raise ValidationFailedError("Qurilma kaliti noto'g'ri",
                                    fields=["device_public_key"]) from None


@router.post("/otp", response_model=OtpSentOut)
async def request_otp(body: OtpRequestIn, request: Request, c: ContainerDep) -> OtpSentOut:
    """Raqam ro'yxatdan o'tgan-o'tmaganidan qat'i nazar bir xil javob (BE-101)."""
    sent = await factories.request_otp(c).execute(RequestOtpCommand(
        phone=body.phone, ip=client_ip(request), installation_id=body.device_id,
        attestation_token=body.attestation_token))
    return OtpSentOut(resend_after=sent.resend_after, expires_in=sent.expires_in)


@router.post("/verify", response_model=VerifyOut)
async def verify_otp(body: OtpVerifyIn, request: Request, c: ContainerDep,
                     tokens: TokenIssuerDep) -> VerifyOut:
    result = await VerifyOtp(
        c.uow(), c.kv, c.limiter, c.hasher, c.cipher, c.key_verifier, tokens,
        c.notifier, c.clock, c.settings, c.geo,
    ).execute(VerifyOtpCommand(
        phone=body.phone, code=body.code, ip=client_ip(request),
        installation_id=body.device_id,
        device_public_key=_decode_key(body.device_public_key),
        device_name=body.device_name, platform=body.platform,
        pin_reset=body.purpose is OtpPurpose.PIN_RESET,
    ))
    t = result.tokens
    return VerifyOut(
        access_token=t.access_token, refresh_token=t.refresh_token, expires_in=t.expires_in,
        user=VerifyUserOut(id=result.user_id, first_name=result.first_name,
                           is_new=result.is_new_user, has_pin_setup=result.has_pin_setup,
                           onboarding=OnboardingOut(**result.onboarding)),
    )


@router.post("/refresh", response_model=TokenOut)
async def refresh(body: RefreshIn, proof: DeviceProofDep, c: ContainerDep,
                  tokens: TokenIssuerDep) -> TokenOut:
    """Qurilma kaliti bilan imzolangan (X-Device-Timestamp, X-Device-Signature)."""
    pair = await RefreshTokens(
        c.uow(), c.hasher, c.key_verifier, tokens, c.limiter, c.notifier, c.clock, c.settings,
    ).execute(RefreshCommand(refresh_token=body.refresh_token, proof=proof))
    return TokenOut(access_token=pair.access_token, refresh_token=pair.refresh_token,
                    expires_in=pair.expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(ctx: AuthDep, c: ContainerDep) -> None:
    await Logout(c.uow(), c.clock).execute(ctx)
