from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class Platform(StrEnum):
    IOS = "ios"
    ANDROID = "android"


@dataclass(slots=True)
class Device:
    """Qurilma. installation_id — ilova o'rnatilganda yaratiladigan UUID (mijozda saqlanadi).

    public_key — qurilma Secure Enclave / Android Keystore'dagi P-256 kalitining
    ochiq qismi (DER SubjectPublicKeyInfo). Refresh va sezgir so'rovlar shu kalit bilan imzolanadi.
    """

    id: UUID
    user_id: UUID
    installation_id: UUID
    public_key: bytes
    name: str
    platform: Platform
    created_at: datetime
    last_seen_at: datetime
    # Qurilma darajasidagi holat va sozlamalar (BE-201, BE-205). PIN'ning o'zi serverda yo'q
    has_pin_setup: bool = False
    auto_lock_minutes: int = 1
    biometric_enabled: bool = False
    # Oxirgi kirish shahri (IP geolokatsiya), "New sign-in" matni va qurilmalar ro'yxati uchun
    city: str | None = None


AUTO_LOCK_CHOICES = (1, 3, 5)


class RevokeReason(StrEnum):
    LOGOUT = "logout"
    LOGOUT_ALL = "logout_all"
    REFRESH_REUSE = "refresh_reuse"
    PIN_FAILURES = "pin_failures"
    RELOGIN = "relogin"
    PIN_RESET = "pin_reset"
    ACCOUNT_DELETED = "account_deleted"


@dataclass(slots=True)
class Session:
    """Sessiya = refresh tokenlar oilasi (family). Bekor qilinsa, oiladagi hamma token o'ladi."""

    id: UUID
    user_id: UUID
    device_id: UUID
    created_at: datetime
    revoked_at: datetime | None = None
    revoke_reason: RevokeReason | None = None

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None


@dataclass(slots=True)
class RefreshToken:
    id: UUID
    session_id: UUID
    token_hash: str
    created_at: datetime
    expires_at: datetime
    used_at: datetime | None = None


@dataclass(slots=True)
class OtpChallenge:
    """Kutilayotgan SMS kod. Kodning o'zi emas, HMAC-SHA256 xeshi saqlanadi."""

    phone_index: str
    code_hash: str
    expires_at: datetime
