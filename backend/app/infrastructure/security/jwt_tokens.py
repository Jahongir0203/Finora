"""Access token: JWT ES256, 15 daqiqa. Payload faqat sub, sid, did, exp (+ iat, iss)."""

import logging
import time
from uuid import UUID

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.application.common.interfaces import AccessClaims
from app.core.config import Environment, Settings
from app.domain.common.errors import AuthenticationError

_ALG = "ES256"
logger = logging.getLogger("finora.security")


class Es256AccessTokenService:
    def __init__(self, settings: Settings) -> None:
        if settings.jwt_private_key is not None:
            key = serialization.load_pem_private_key(
                settings.jwt_private_key.get_secret_value().encode(), password=None
            )
            if not isinstance(key, ec.EllipticCurvePrivateKey) or key.curve.name != "secp256r1":
                raise ValueError("JWT kaliti P-256 (ES256) bo'lishi kerak")
        else:
            if settings.env is Environment.PROD:
                raise ValueError("Prod'da JWT kaliti majburiy")
            logger.warning("jwt_ephemeral_key_generated")
            key = ec.generate_private_key(ec.SECP256R1())
        self._private = key
        self._public = key.public_key()
        self._ttl = settings.access_token_ttl_seconds
        self._issuer = settings.jwt_issuer

    def issue(self, user_id: UUID, session_id: UUID, device_id: UUID) -> tuple[str, int]:
        now = int(time.time())
        payload = {
            "sub": str(user_id),
            "sid": str(session_id),
            "did": str(device_id),
            "iat": now,
            "exp": now + self._ttl,
            "iss": self._issuer,
        }
        return jwt.encode(payload, self._private, algorithm=_ALG), self._ttl

    def decode(self, token: str) -> AccessClaims:
        try:
            data = jwt.decode(
                token,
                self._public,
                algorithms=[_ALG],  # "none" va HS* algoritmlari rad etiladi
                issuer=self._issuer,
                options={"require": ["sub", "sid", "did", "exp", "iss"]},
            )
            return AccessClaims(sub=UUID(data["sub"]), sid=UUID(data["sid"]),
                                did=UUID(data["did"]), exp=int(data["exp"]))
        except (jwt.PyJWTError, ValueError, KeyError):
            raise AuthenticationError() from None
