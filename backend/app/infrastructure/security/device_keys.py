"""Qurilma kaliti: ECDSA P-256 (iOS Secure Enclave va Android Keystore qo'llaydi)."""

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.domain.common.errors import ValidationFailedError

MAX_KEY_BYTES = 512


def _load(public_key: bytes) -> ec.EllipticCurvePublicKey:
    if len(public_key) > MAX_KEY_BYTES:
        raise ValidationFailedError("Qurilma kaliti noto'g'ri")
    try:
        key = serialization.load_der_public_key(public_key)
    except (ValueError, TypeError):
        raise ValidationFailedError("Qurilma kaliti noto'g'ri") from None
    if not isinstance(key, ec.EllipticCurvePublicKey) or key.curve.name != "secp256r1":
        raise ValidationFailedError("Qurilma kaliti P-256 bo'lishi kerak")
    return key


class EcdsaP256Verifier:
    def validate_public_key(self, public_key: bytes) -> None:
        _load(public_key)

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        try:
            _load(public_key).verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except (InvalidSignature, ValidationFailedError, ValueError):
            return False
