"""Field-level shifrlash: AES-256-GCM (02-backend.md, 5-bo'lim).

Format: 1 bayt versiya | 12 bayt nonce | ciphertext+tag.
Versiya kalit almashtirish (yillik rotatsiya) uchun — eski versiyalar o'qiladi.
Prod'da kalit KMS'dan (envelope encryption) keladi.
"""

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import Settings
from app.domain.common.values import PhoneNumber

_VERSION = 1
_AAD = b"finora:user.phone"


class AesGcmPhoneCipher:
    def __init__(self, settings: Settings) -> None:
        key = base64.b64decode(settings.field_encryption_key.get_secret_value())
        if len(key) != 32:
            raise ValueError("FINORA_FIELD_ENCRYPTION_KEY 32 bayt (base64) bo'lishi kerak")
        self._keys = {_VERSION: AESGCM(key)}

    def encrypt(self, phone: PhoneNumber) -> bytes:
        nonce = os.urandom(12)
        ct = self._keys[_VERSION].encrypt(nonce, phone.value.encode(), _AAD)
        return bytes([_VERSION]) + nonce + ct

    def decrypt(self, ciphertext: bytes) -> PhoneNumber:
        version, nonce, ct = ciphertext[0], ciphertext[1:13], ciphertext[13:]
        return PhoneNumber(self._keys[version].decrypt(nonce, ct, _AAD).decode())
