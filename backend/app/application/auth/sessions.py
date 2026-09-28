"""Tokenlar, sessiyalar va qurilmalar (02-backend.md, 2 va 7-bo'limlar)."""

import logging
from uuid import UUID

from app.application.auth.dto import (
    AuthContext,
    DeviceView,
    PinFailuresCommand,
    RefreshCommand,
    TokenPair,
)
from app.application.auth.tokens import TokenIssuer
from app.application.common.audit import record_audit
from app.application.common.device_proof import verify_device_proof
from app.application.common.interfaces import (
    AccessTokenService,
    Clock,
    DeviceKeyVerifier,
    Notifier,
    SecretHasher,
)
from app.application.common.rate_limit import HOUR, Limit, RateLimiter
from app.application.common.uow import UnitOfWork
from app.core.config import Settings
from app.domain.audit.entities import AuditAction
from app.domain.auth.entities import RefreshToken, RevokeReason, Session
from app.domain.common.errors import (
    AuthenticationError,
    NotFoundError,
    TokenReuseDetectedError,
)

logger = logging.getLogger("finora.auth")


class Authenticate:
    """Access tokenni tekshiradi va sessiya hali faolligini tasdiqlaydi.

    Sessiya tekshiruvi logout / "barcha qurilmalardan chiqish" darhol kuchga kirishi uchun.
    """

    def __init__(self, uow: UnitOfWork, access_tokens: AccessTokenService) -> None:
        self._uow = uow
        self._access = access_tokens

    async def execute(self, token: str) -> AuthContext:
        claims = self._access.decode(token)
        async with self._uow as uow:
            session = await uow.sessions.get(claims.sid)
        if (
            session is None
            or not session.is_active
            or session.user_id != claims.sub
            or session.device_id != claims.did
        ):
            raise AuthenticationError()
        return AuthContext(user_id=claims.sub, session_id=claims.sid, device_id=claims.did)


class _SessionLookup:
    def __init__(self, hasher: SecretHasher) -> None:
        self._hasher = hasher

    async def _load(self, uow: UnitOfWork, raw_token: str) -> tuple[RefreshToken, Session]:
        token = await uow.refresh_tokens.get_by_hash(self._hasher.token_hash(raw_token))
        if token is None:
            raise AuthenticationError()
        session = await uow.sessions.get(token.session_id)
        if session is None or not session.is_active:
            raise AuthenticationError()
        return token, session


class RefreshTokens(_SessionLookup):
    def __init__(
        self,
        uow: UnitOfWork,
        hasher: SecretHasher,
        key_verifier: DeviceKeyVerifier,
        tokens: TokenIssuer,
        limiter: RateLimiter,
        notifier: Notifier,
        clock: Clock,
        settings: Settings,
    ) -> None:
        super().__init__(hasher)
        self._uow = uow
        self._key_verifier = key_verifier
        self._tokens = tokens
        self._limiter = limiter
        self._notifier = notifier
        self._clock = clock
        self._s = settings

    async def execute(self, cmd: RefreshCommand) -> TokenPair:
        now = self._clock.now()
        async with self._uow as uow:
            token, session = await self._load(uow, cmd.refresh_token)
            await self._limiter.hit(
                "refresh", str(session.id), [Limit("hour", self._s.refresh_per_hour, HOUR)]
            )

            if token.used_at is not None:
                await self._revoke_family(uow, session)
                raise TokenReuseDetectedError()
            if now >= token.expires_at:
                raise AuthenticationError()

            device = await uow.devices.get_for_user(session.user_id, session.device_id)
            if device is None:
                raise AuthenticationError()
            verify_device_proof(
                self._key_verifier, device.public_key, cmd.proof, now,
                self._s.device_signature_window_seconds,
            )

            if not await uow.refresh_tokens.mark_used(token.id, now):
                # Parallel so'rov shu tokenni allaqachon ishlatdi — bu ham reuse
                await self._revoke_family(uow, session)
                raise TokenReuseDetectedError()

            device.last_seen_at = now
            await uow.devices.update(device)
            pair = await self._tokens.issue(uow, session)
            await uow.commit()
            return pair

    async def _revoke_family(self, uow: UnitOfWork, session: Session) -> None:
        now = self._clock.now()
        await uow.sessions.revoke(session.id, RevokeReason.REFRESH_REUSE, now)
        await record_audit(uow, self._clock, AuditAction.REFRESH_REUSE,
                           user_id=session.user_id, device_id=session.device_id)
        await uow.commit()
        logger.warning("refresh_token_reuse", extra={"event": "alert.refresh_reuse"})
        await self._notifier.sessions_revoked(session.user_id, reason="new_sign_in")


class Logout:
    """Server tomonida refresh oilasini bekor qiladi (faqat mijozda o'chirish yetarli emas)."""

    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    async def execute(self, ctx: AuthContext) -> None:
        async with self._uow as uow:
            await uow.sessions.revoke(ctx.session_id, RevokeReason.LOGOUT, self._clock.now())
            await record_audit(uow, self._clock, AuditAction.LOGOUT,
                               user_id=ctx.user_id, device_id=ctx.device_id)
            await uow.commit()


class LogoutAll:
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    async def execute(self, ctx: AuthContext) -> None:
        async with self._uow as uow:
            await uow.sessions.revoke_all_for_user(
                ctx.user_id, RevokeReason.LOGOUT_ALL, self._clock.now()
            )
            await record_audit(uow, self._clock, AuditAction.LOGOUT_ALL,
                               user_id=ctx.user_id, device_id=ctx.device_id)
            await uow.commit()


class ListDevices:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, ctx: AuthContext) -> list[DeviceView]:
        async with self._uow as uow:
            active = {s.device_id for s in await uow.sessions.list_active_for_user(ctx.user_id)}
            devices = await uow.devices.list_for_user(ctx.user_id)
        return [
            DeviceView(
                id=d.id,
                name=d.name,
                platform=d.platform,
                created_at=d.created_at,
                last_seen_at=d.last_seen_at,
                is_current=d.id == ctx.device_id,
            )
            for d in devices
            if d.id in active
        ]


class SignOutDevice:
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    async def execute(self, ctx: AuthContext, device_id: UUID) -> None:
        async with self._uow as uow:
            device = await uow.devices.get_for_user(ctx.user_id, device_id)
            if device is None:
                raise NotFoundError()
            await uow.sessions.revoke_for_device(
                ctx.user_id, device.id, RevokeReason.LOGOUT, self._clock.now()
            )
            await record_audit(uow, self._clock, AuditAction.LOGOUT, user_id=ctx.user_id,
                               device_id=device.id, initiated_by=str(ctx.device_id))
            await uow.commit()


class ReportPinFailures(_SessionLookup):
    """Mijoz 5 xato PIN haqida xabar beradi.

    So'rov qurilma kaliti bilan imzolangan bo'lishi shart.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        hasher: SecretHasher,
        key_verifier: DeviceKeyVerifier,
        notifier: Notifier,
        clock: Clock,
        settings: Settings,
    ) -> None:
        super().__init__(hasher)
        self._uow = uow
        self._key_verifier = key_verifier
        self._notifier = notifier
        self._clock = clock
        self._s = settings

    async def execute(self, cmd: PinFailuresCommand) -> None:
        now = self._clock.now()
        async with self._uow as uow:
            _, session = await self._load(uow, cmd.refresh_token)
            device = await uow.devices.get_for_user(session.user_id, session.device_id)
            if device is None:
                raise AuthenticationError()
            verify_device_proof(
                self._key_verifier, device.public_key, cmd.proof, now,
                self._s.device_signature_window_seconds,
            )
            await uow.sessions.revoke_for_device(
                session.user_id, device.id, RevokeReason.PIN_FAILURES, now
            )
            await record_audit(uow, self._clock, AuditAction.PIN_FAILURES,
                               user_id=session.user_id, device_id=device.id, ip=cmd.ip)
            await uow.commit()
        await self._notifier.sessions_revoked(session.user_id, reason="pin_failures")
