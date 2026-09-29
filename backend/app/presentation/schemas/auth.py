from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, StringConstraints

from app.domain.auth.entities import Platform
from app.presentation.schemas.common import Name, StrictModel

Phone = Annotated[str, StringConstraints(min_length=9, max_length=20)]
OtpCode = Annotated[str, StringConstraints(pattern=r"^\d{6}$")]
Base64Key = Annotated[str, StringConstraints(min_length=40, max_length=700,
                                             pattern=r"^[A-Za-z0-9_\-+/=]+$")]
OpaqueToken = Annotated[str, StringConstraints(min_length=20, max_length=128)]
AttestationToken = Annotated[str, StringConstraints(min_length=16, max_length=8192)]


class OtpPurpose(StrEnum):
    LOGIN = "login"
    PIN_RESET = "pin_reset"


class OtpRequestIn(StrictModel):
    phone: Phone
    # Ilova o'rnatilganda yaratiladigan UUID (installation id)
    device_id: UUID
    attestation_token: AttestationToken | None = None
    # "sms" — Telegram ulangan bo'lsa ham SMS ("SMS orqali yuborish" tugmasi)
    channel: Literal["auto", "sms"] = "auto"


class OtpSentOut(BaseModel):
    resend_after: int
    expires_in: int
    # Kodni Telegram'da olish uchun bot havolasi (bot sozlanmagan bo'lsa null). Javob har
    # doim bir xil: kod qaysi kanalga ketgani oshkor qilinmaydi (02-backend.md, 1-bo'lim)
    telegram_bot_url: str | None = None


class OtpVerifyIn(StrictModel):
    phone: Phone
    code: OtpCode
    device_id: UUID
    device_public_key: Base64Key
    device_name: Name
    platform: Platform
    purpose: OtpPurpose = OtpPurpose.LOGIN


class RefreshIn(StrictModel):
    refresh_token: OpaqueToken


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105 — OAuth2 token turi, secret emas
    expires_in: int


class OnboardingOut(BaseModel):
    balance_set: bool
    has_transactions: bool
    has_goals: bool
    has_reminders: bool


class VerifyUserOut(BaseModel):
    id: UUID
    first_name: str | None
    is_new: bool
    has_pin_setup: bool
    onboarding: OnboardingOut


class VerifyOut(TokenOut):
    user: VerifyUserOut


class DeviceOut(BaseModel):
    id: UUID
    name: str
    platform: Platform
    city: str | None
    last_active_at: datetime
    created_at: datetime
    current: bool
