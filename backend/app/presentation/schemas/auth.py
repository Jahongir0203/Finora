from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, StringConstraints

from app.domain.auth.entities import Platform
from app.presentation.schemas.common import Name, StrictModel

Phone = Annotated[str, StringConstraints(min_length=9, max_length=20)]
OtpCode = Annotated[str, StringConstraints(pattern=r"^\d{6}$")]
Base64Key = Annotated[str, StringConstraints(min_length=40, max_length=700,
                                             pattern=r"^[A-Za-z0-9_\-+/=]+$")]
OpaqueToken = Annotated[str, StringConstraints(min_length=20, max_length=128)]


class OtpRequestIn(StrictModel):
    phone: Phone
    installation_id: UUID


class OtpVerifyIn(StrictModel):
    phone: Phone
    code: OtpCode
    installation_id: UUID
    device_public_key: Base64Key
    device_name: Name
    platform: Platform
    pin_reset: bool = False


class RefreshIn(StrictModel):
    refresh_token: OpaqueToken


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105 — OAuth2 token turi, secret emas
    expires_in: int


class VerifyOut(TokenOut):
    is_new_user: bool


class DeviceOut(BaseModel):
    id: UUID
    name: str
    platform: Platform
    created_at: datetime
    last_seen_at: datetime
    is_current: bool
