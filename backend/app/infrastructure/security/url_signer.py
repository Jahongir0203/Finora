"""Imzolangan URL: HMAC-SHA256(resource:expires_at).

Muddat imzoga kiradi — uni o'zgartirib bo'lmaydi.
"""

import base64
import hashlib
import hmac

from app.core.config import Settings


class HmacUrlSigner:
    def __init__(self, settings: Settings) -> None:
        self._key = settings.url_signing_key.get_secret_value().encode()

    def sign(self, resource: str, expires_at: int) -> str:
        mac = hmac.new(self._key, f"{resource}:{expires_at}".encode(), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(mac).decode().rstrip("=")

    def verify(self, resource: str, expires_at: int, signature: str, now: int) -> bool:
        if now >= expires_at:
            return False
        return hmac.compare_digest(self.sign(resource, expires_at), signature)
