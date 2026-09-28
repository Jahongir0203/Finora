"""Qurilma kaliti bilan imzolangan so'rovlar (02-backend.md, 2 va 7-bo'limlar).

Kanonik xabar:  METHOD \n PATH \n TIMESTAMP \n SHA256(body) hex
Imzo: ECDSA P-256 / SHA-256, DER, base64url.
"""

import base64
import binascii
import hashlib
from dataclasses import dataclass
from datetime import datetime

from app.application.common.interfaces import DeviceKeyVerifier
from app.domain.common.errors import InvalidDeviceSignatureError


@dataclass(frozen=True, slots=True)
class DeviceProof:
    method: str
    path: str
    timestamp: str
    body: bytes
    signature_b64: str


def canonical_message(proof: DeviceProof) -> bytes:
    body_hash = hashlib.sha256(proof.body).hexdigest()
    return f"{proof.method.upper()}\n{proof.path}\n{proof.timestamp}\n{body_hash}".encode()


def verify_device_proof(
    verifier: DeviceKeyVerifier,
    public_key: bytes,
    proof: DeviceProof,
    now: datetime,
    window_seconds: int,
) -> None:
    try:
        ts = int(proof.timestamp)
    except ValueError:
        raise InvalidDeviceSignatureError() from None
    if abs(now.timestamp() - ts) > window_seconds:
        raise InvalidDeviceSignatureError()
    try:
        padded = proof.signature_b64 + "=" * (-len(proof.signature_b64) % 4)
        signature = base64.urlsafe_b64decode(padded)
    except (binascii.Error, ValueError):
        raise InvalidDeviceSignatureError() from None
    if not verifier.verify(public_key, canonical_message(proof), signature):
        raise InvalidDeviceSignatureError()
