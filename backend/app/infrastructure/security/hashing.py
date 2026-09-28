"""HMAC-SHA256 — har bir maqsad uchun alohida kalit (02-backend.md, 1, 2, 5-bo'limlar)."""

import hashlib
import hmac

from app.core.config import Settings
from app.domain.common.values import PhoneNumber


class HmacHasher:
    def __init__(self, settings: Settings) -> None:
        self._otp_key = settings.otp_hmac_key.get_secret_value().encode()
        self._index_key = settings.blind_index_key.get_secret_value().encode()
        self._token_key = settings.refresh_token_pepper.get_secret_value().encode()

    @staticmethod
    def _hmac(key: bytes, value: str) -> str:
        return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()

    def otp_hash(self, phone_index: str, code: str) -> str:
        return self._hmac(self._otp_key, f"{phone_index}:{code}")

    def phone_index(self, phone: PhoneNumber) -> str:
        """Blind index: shifrlangan telefonni qidirish uchun deterministik HMAC."""
        return self._hmac(self._index_key, phone.value)

    def token_hash(self, token: str) -> str:
        return self._hmac(self._token_key, token)

    def constant_time_equals(self, a: str, b: str) -> bool:
        return hmac.compare_digest(a.encode(), b.encode())
