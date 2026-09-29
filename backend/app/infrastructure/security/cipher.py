"""Field-level shifrlash: AES-256-GCM (02-backend.md, 5-bo'lim).

Format: 1 bayt versiya | 12 bayt nonce | ciphertext+tag.
Yillik kalit almashtirish:
  1. FINORA_FIELD_ENCRYPTION_KEY — yangi kalit, FINORA_FIELD_ENCRYPTION_KEY_VERSION — yangi
     versiya (masalan 2); eski kalit FINORA_FIELD_ENCRYPTION_KEYS_PREVIOUS="1:<base64>".
  2. `python -m app.jobs reencrypt-phones` — barcha yozuvlar yangi kalitga o'tkaziladi.
  3. Eski kalit PREVIOUS ro'yxatidan olib tashlanadi.
Prod'da kalitlar KMS'dan (envelope encryption) keladi.
"""

import base64
import binascii
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import Settings
from app.domain.common.values import PhoneNumber

_AAD = b"finora:user.phone"


def _key(b64: str, name: str) -> AESGCM:
    try:
        key = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError(f"{name} base64 bo'lishi kerak") from None
    if len(key) != 32:
        raise ValueError(f"{name} 32 bayt (base64) bo'lishi kerak")
    return AESGCM(key)


class AesGcmPhoneCipher:
    def __init__(self, settings: Settings) -> None:
        self._version = settings.field_encryption_key_version
        if not 1 <= self._version <= 255:
            raise ValueError("FINORA_FIELD_ENCRYPTION_KEY_VERSION 1..255")
        self._keys = {self._version: _key(settings.field_encryption_key.get_secret_value(),
                                          "FINORA_FIELD_ENCRYPTION_KEY")}
        previous = settings.field_encryption_keys_previous
        for item in (previous.get_secret_value().split(",") if previous else []):
            version, _, b64 = item.strip().partition(":")
            if not version.isdigit() or int(version) == self._version:
                raise ValueError("FINORA_FIELD_ENCRYPTION_KEYS_PREVIOUS: 'versiya:base64,...'")
            self._keys[int(version)] = _key(b64, f"eski kalit v{version}")

    @property
    def current_version(self) -> int:
        return self._version

    def encrypt(self, phone: PhoneNumber) -> bytes:
        nonce = os.urandom(12)
        ct = self._keys[self._version].encrypt(nonce, phone.value.encode(), _AAD)
        return bytes([self._version]) + nonce + ct

    def decrypt(self, ciphertext: bytes) -> PhoneNumber:
        version, nonce, ct = ciphertext[0], ciphertext[1:13], ciphertext[13:]
        return PhoneNumber(self._keys[version].decrypt(nonce, ct, _AAD).decode())

    def needs_rotation(self, ciphertext: bytes) -> bool:
        return ciphertext[0] != self._version
