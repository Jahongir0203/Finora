"""SMS OTP: so'rash va tasdiqlash (02-backend.md, 1-bo'lim)."""

import json
import logging
import secrets
from datetime import datetime, timedelta

from app.application.auth.dto import (
    RequestOtpCommand,
    VerifyOtpCommand,
    VerifyOtpResult,
)
from app.application.auth.tokens import TokenIssuer
from app.application.common.audit import record_audit
from app.application.common.interfaces import (
    Clock,
    DeviceKeyVerifier,
    KeyValueStore,
    Notifier,
    PhoneCipher,
    SecretHasher,
    SmsSender,
)
from app.application.common.rate_limit import DAY, HOUR, Limit, RateLimiter
from app.application.common.uow import UnitOfWork
from app.core.config import Settings
from app.domain.audit.entities import AuditAction
from app.domain.auth.entities import Device, OtpChallenge, RevokeReason, Session
from app.domain.common.errors import InvalidOtpError, OtpBlockedError, RateLimitedError
from app.domain.common.ids import uuid7
from app.domain.common.values import PhoneNumber, ensure_name
from app.domain.users.entities import User

logger = logging.getLogger("finora.auth")


def _challenge_key(phone_index: str) -> str:
    return f"otp:ch:{phone_index}"


def _attempts_key(phone_index: str) -> str:
    return f"otp:att:{phone_index}"


def _block_key(phone_index: str) -> str:
    return f"otp:block:{phone_index}"


async def _ensure_not_blocked(store: KeyValueStore, phone_index: str) -> None:
    ttl = await store.ttl(_block_key(phone_index))
    if ttl > 0:
        raise OtpBlockedError(retry_after=ttl)


class RequestOtp:
    def __init__(
        self,
        store: KeyValueStore,
        limiter: RateLimiter,
        hasher: SecretHasher,
        sms: SmsSender,
        clock: Clock,
        settings: Settings,
    ) -> None:
        self._store = store
        self._limiter = limiter
        self._hasher = hasher
        self._sms = sms
        self._clock = clock
        self._s = settings

    async def execute(self, cmd: RequestOtpCommand) -> None:
        """Javob har doim bir xil — raqam ro'yxatdan o'tgan-o'tmagani oshkor qilinmaydi."""
        phone = PhoneNumber.parse(cmd.phone)
        idx = self._hasher.phone_index(phone)
        await _ensure_not_blocked(self._store, idx)

        s = self._s
        subject_limits = [
            Limit("resend", 1, s.otp_resend_seconds),
            Limit("hour", s.otp_per_hour, HOUR),
            Limit("day", s.otp_per_day, DAY),
        ]
        await self._limiter.hit_many(
            "otp", [f"p:{idx}", f"d:{cmd.installation_id}"], subject_limits
        )
        try:
            await self._limiter.hit(
                "otp",
                f"ip:{cmd.ip}",
                [Limit("ip_hour", s.otp_ip_per_hour, HOUR), Limit("ip_day", s.otp_ip_per_day, DAY)],
            )
        except RateLimitedError:
            # Alert: bitta IP'dan ko'p raqam (02-backend.md, 9-bo'lim)
            logger.warning("otp_ip_limit_exceeded", extra={"event": "alert.otp_ip_flood"})
            raise

        code = f"{secrets.randbelow(10**s.otp_length):0{s.otp_length}d}"
        challenge = OtpChallenge(
            phone_index=idx,
            code_hash=self._hasher.otp_hash(idx, code),
            expires_at=self._clock.now() + timedelta(seconds=s.otp_ttl_seconds),
        )
        await self._store.set(
            _challenge_key(idx),
            json.dumps({"h": challenge.code_hash, "exp": challenge.expires_at.timestamp()}),
            s.otp_ttl_seconds,
        )
        # Yangi kod — yangi urinishlar hisobi
        await self._store.delete(_attempts_key(idx))
        await self._sms.send(phone, f"Finora: tasdiqlash kodi {code}. Uni hech kimga aytmang.")
        logger.info("otp_sent")


class VerifyOtp:
    def __init__(
        self,
        uow: UnitOfWork,
        store: KeyValueStore,
        limiter: RateLimiter,
        hasher: SecretHasher,
        cipher: PhoneCipher,
        key_verifier: DeviceKeyVerifier,
        tokens: TokenIssuer,
        notifier: Notifier,
        clock: Clock,
        settings: Settings,
    ) -> None:
        self._uow = uow
        self._store = store
        self._limiter = limiter
        self._hasher = hasher
        self._cipher = cipher
        self._key_verifier = key_verifier
        self._tokens = tokens
        self._notifier = notifier
        self._clock = clock
        self._s = settings

    async def execute(self, cmd: VerifyOtpCommand) -> VerifyOtpResult:
        phone = PhoneNumber.parse(cmd.phone)
        idx = self._hasher.phone_index(phone)
        await _ensure_not_blocked(self._store, idx)
        await self._limiter.hit_many(
            "otp_verify",
            [f"p:{idx}", f"ip:{cmd.ip}"],
            [Limit("hour", self._s.otp_verify_per_hour, HOUR)],
        )
        await self._check_code(idx, cmd.code)

        self._key_verifier.validate_public_key(cmd.device_public_key)
        device_name = ensure_name(cmd.device_name)
        now = self._clock.now()

        async with self._uow as uow:
            user = await uow.users.get_by_phone_index(idx)
            is_new_user = user is None
            if user is None:
                user = User(
                    id=uuid7(),
                    phone_ciphertext=self._cipher.encrypt(phone),
                    phone_index=idx,
                    created_at=now,
                )
                await uow.users.add(user)

            device = await uow.devices.get_by_installation(user.id, cmd.installation_id)
            is_new_device = device is None
            if device is None:
                device = Device(
                    id=uuid7(),
                    user_id=user.id,
                    installation_id=cmd.installation_id,
                    public_key=cmd.device_public_key,
                    name=device_name,
                    platform=cmd.platform,
                    created_at=now,
                    last_seen_at=now,
                )
                await uow.devices.add(device)
            else:
                # Qayta kirish / "Forgot PIN?": shu qurilmaning eski sessiyalari bekor qilinadi,
                # qurilma kaliti yangilanadi (02-backend.md, 7-bo'lim)
                reason = RevokeReason.RELOGIN
                await uow.sessions.revoke_for_device(user.id, device.id, reason, now)
                device.public_key = cmd.device_public_key
                device.name = device_name
                device.platform = cmd.platform
                device.last_seen_at = now
                await uow.devices.update(device)

            session = Session(id=uuid7(), user_id=user.id, device_id=device.id, created_at=now)
            await uow.sessions.add(session)
            tokens = await self._tokens.issue(uow, session)

            await record_audit(uow, self._clock, AuditAction.LOGIN, user_id=user.id,
                               device_id=device.id, ip=cmd.ip)
            if is_new_device and not is_new_user:
                await record_audit(uow, self._clock, AuditAction.NEW_DEVICE, user_id=user.id,
                                   device_id=device.id, ip=cmd.ip)
            if cmd.pin_reset:
                await record_audit(uow, self._clock, AuditAction.PIN_RESET, user_id=user.id,
                                   device_id=device.id, ip=cmd.ip)
            await uow.commit()

        if is_new_device and not is_new_user:
            await self._notifier.new_sign_in(user.id, exclude_device_id=device.id,
                                             device_name=device.name)
        return VerifyOtpResult(tokens=tokens, is_new_user=is_new_user)

    async def _check_code(self, idx: str, code: str) -> None:
        raw = await self._store.get(_challenge_key(idx))
        if raw is None:
            raise InvalidOtpError()
        data = json.loads(raw)
        if self._clock.now() >= datetime.fromtimestamp(data["exp"], tz=self._clock.now().tzinfo):
            await self._store.delete(_challenge_key(idx))
            raise InvalidOtpError()

        attempts, _ = await self._store.incr(_attempts_key(idx), self._s.otp_ttl_seconds)
        candidate = self._hasher.otp_hash(idx, code) if code.isdigit() else ""
        if candidate and self._hasher.constant_time_equals(candidate, data["h"]):
            # Bir martalik: faqat birinchi muvaffaqiyatli so'rov kodni "yeydi"
            if not await self._store.delete(_challenge_key(idx)):
                raise InvalidOtpError()
            await self._store.delete(_attempts_key(idx))
            return

        if attempts >= self._s.otp_max_attempts:
            await self._store.delete(_challenge_key(idx))
            await self._store.set(_block_key(idx), "1", self._s.otp_block_seconds)
            logger.warning("otp_blocked", extra={"event": "alert.otp_failures"})
            raise OtpBlockedError(retry_after=self._s.otp_block_seconds)
        logger.info("otp_invalid")
        raise InvalidOtpError()
