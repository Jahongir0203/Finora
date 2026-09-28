"""Tashqi xizmatlar uchun portlar. Implementatsiyalar infrastructure qatlamida."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from app.domain.common.values import PhoneNumber
from app.domain.notifications.entities import PushProvider


class Clock(Protocol):
    def now(self) -> datetime: ...


class KeyValueStore(Protocol):
    """Redis-simon TTL'li kalit-qiymat ombori (rate limit, OTP, bloklar)."""

    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl_seconds: int) -> None: ...
    async def delete(self, key: str) -> bool:
        """Atomar o'chirish. Kalit mavjud bo'lgan bo'lsa True."""
        ...
    async def incr(self, key: str, ttl_seconds: int) -> tuple[int, int]:
        """Hisoblagichni oshiradi. (yangi qiymat, qolgan TTL soniyalarda) qaytaradi.
        TTL faqat birinchi incr'da o'rnatiladi (fixed window)."""
        ...
    async def ttl(self, key: str) -> int: ...


class SecretHasher(Protocol):
    """Kalitli HMAC-SHA256. Har bir maqsad uchun alohida kalit."""

    def otp_hash(self, phone_index: str, code: str) -> str: ...
    def phone_index(self, phone: PhoneNumber) -> str: ...
    def token_hash(self, token: str) -> str: ...
    def constant_time_equals(self, a: str, b: str) -> bool: ...


class PhoneCipher(Protocol):
    def encrypt(self, phone: PhoneNumber) -> bytes: ...
    def decrypt(self, ciphertext: bytes) -> PhoneNumber: ...


@dataclass(frozen=True, slots=True)
class AccessClaims:
    sub: UUID
    sid: UUID
    did: UUID
    exp: int


class AccessTokenService(Protocol):
    def issue(self, user_id: UUID, session_id: UUID, device_id: UUID) -> tuple[str, int]:
        """(token, expires_in) qaytaradi."""
        ...
    def decode(self, token: str) -> AccessClaims:
        """Imzo va muddatni tekshiradi. Xato bo'lsa AuthenticationError."""
        ...


class DeviceKeyVerifier(Protocol):
    def validate_public_key(self, public_key: bytes) -> None:
        """P-256 kaliti ekanini tekshiradi, aks holda ValidationFailedError."""
        ...
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool: ...


class SmsSender(Protocol):
    async def send(self, phone: PhoneNumber, text: str) -> None: ...


class Notifier(Protocol):
    """Push va ilova ichidagi bildirishnomalar."""

    async def new_sign_in(
        self, user_id: UUID, exclude_device_id: UUID, device_name: str
    ) -> None: ...
    async def sessions_revoked(self, user_id: UUID, reason: str) -> None: ...


class FileStorage(Protocol):
    """Yopiq (private) fayl ombori — S3 yoki mahalliy disk."""

    async def put(self, key: str, data: bytes, content_type: str) -> None: ...
    async def get(self, key: str) -> bytes | None: ...
    async def delete(self, key: str) -> None: ...
    async def presigned_get_url(self, key: str, ttl_seconds: int) -> str | None:
        """Ombor o'zi imzolangan URL bera olsa (S3) — URL, aks holda None (HMAC endpoint)."""
        ...


class MalwareScanner(Protocol):
    async def is_clean(self, data: bytes) -> bool:
        """Antivirus skani. Skaner ishlamasa istisno ko'taradi (fail-closed)."""
        ...


@dataclass(frozen=True, slots=True)
class SanitizedImage:
    data: bytes
    content_type: str


class ImageSanitizer(Protocol):
    def sanitize(self, data: bytes, expected_format: str) -> SanitizedImage:
        """Rasmni qayta kodlaydi: EXIF/GPS va boshqa metadata olib tashlanadi.
        Buzilgan yoki haddan katta rasm — FileRejectedError."""
        ...


class UrlSigner(Protocol):
    """Qisqa muddatli imzolangan havolalar (prod'da S3 presigned URL bilan almashtiriladi)."""

    def sign(self, resource: str, expires_at: int) -> str: ...
    def verify(self, resource: str, expires_at: int, signature: str, now: int) -> bool: ...


class InsightsModel(Protocol):
    """AI provayderi. Faqat matn qaytaradi — tool call'lar ishlatilmaydi."""

    async def complete(self, system: str, prompt: str) -> str: ...


class PushSendResult(StrEnum):
    OK = "ok"
    # Ilova o'chirilgan / token eskirgan — bazadan olinadi
    INVALID_TOKEN = "invalid_token"  # noqa: S105 — holat nomi, secret emas
    FAILED = "failed"


class PushSender(Protocol):
    async def send(self, provider: PushProvider, token: str, title: str,
                   body: str) -> PushSendResult: ...
