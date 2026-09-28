from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.device_proof import DeviceProof
from app.domain.auth.entities import Platform


@dataclass(frozen=True, slots=True)
class AuthContext:
    """Autentifikatsiyalangan so'rov egasi. Barcha resurslar shu user_id bilan filtrlanadi."""

    user_id: UUID
    session_id: UUID
    device_id: UUID


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass(frozen=True, slots=True)
class RequestOtpCommand:
    phone: str
    ip: str
    installation_id: UUID


@dataclass(frozen=True, slots=True)
class VerifyOtpCommand:
    phone: str
    code: str
    ip: str
    installation_id: UUID
    device_public_key: bytes
    device_name: str
    platform: Platform
    pin_reset: bool = False


@dataclass(frozen=True, slots=True)
class VerifyOtpResult:
    tokens: TokenPair
    is_new_user: bool


@dataclass(frozen=True, slots=True)
class RefreshCommand:
    refresh_token: str
    proof: DeviceProof


@dataclass(frozen=True, slots=True)
class PinFailuresCommand:
    refresh_token: str
    proof: DeviceProof
    ip: str


@dataclass(frozen=True, slots=True)
class DeviceView:
    id: UUID
    name: str
    platform: Platform
    created_at: datetime
    last_seen_at: datetime
    is_current: bool
