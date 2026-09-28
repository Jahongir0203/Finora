import secrets
from datetime import timedelta

from app.application.auth.dto import TokenPair
from app.application.common.interfaces import AccessTokenService, Clock, SecretHasher
from app.application.common.uow import UnitOfWork
from app.core.config import Settings
from app.domain.auth.entities import RefreshToken, Session
from app.domain.common.ids import uuid7


class TokenIssuer:
    """Access (JWT ES256, 15 daq) + refresh (opaque 256 bit, 30 kun, bazada xesh)."""

    def __init__(
        self,
        access_tokens: AccessTokenService,
        hasher: SecretHasher,
        clock: Clock,
        settings: Settings,
    ) -> None:
        self._access = access_tokens
        self._hasher = hasher
        self._clock = clock
        self._settings = settings

    async def issue(self, uow: UnitOfWork, session: Session) -> TokenPair:
        now = self._clock.now()
        raw_refresh = secrets.token_urlsafe(32)  # 256 bit CSPRNG
        await uow.refresh_tokens.add(
            RefreshToken(
                id=uuid7(),
                session_id=session.id,
                token_hash=self._hasher.token_hash(raw_refresh),
                created_at=now,
                expires_at=now + timedelta(seconds=self._settings.refresh_token_ttl_seconds),
            )
        )
        access, expires_in = self._access.issue(session.user_id, session.id, session.device_id)
        return TokenPair(access_token=access, refresh_token=raw_refresh, expires_in=expires_in)
