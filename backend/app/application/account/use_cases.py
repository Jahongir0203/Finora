"""Akkauntni o'chirish (BE-1304; 01-umumiy.md, 5; 02-backend.md, 5-bo'lim).

Qayta OTP tasdig'i talab qilinadi: avval `POST /v1/me/delete-code` (SMS), keyin
`DELETE /v1/me {code}`. Shaxsiy ma'lumotlar darhol o'chiriladi (30 kunlik talabdan
qattiqroq). Zaxiralardan navbatdagi aylanishda. Audit logda faqat user_id qoladi.
"""

from app.application.auth.dto import AuthContext, OtpSent
from app.application.auth.otp import OtpChecker, RequestOtp
from app.application.common.audit import record_audit
from app.application.common.interfaces import Clock, FileStorage, PhoneCipher
from app.application.common.uow import UnitOfWork
from app.domain.audit.entities import AuditAction
from app.domain.auth.entities import RevokeReason
from app.domain.common.errors import NotFoundError


class SendDeletionCode:
    def __init__(self, uow: UnitOfWork, cipher: PhoneCipher, otp: RequestOtp) -> None:
        self._uow = uow
        self._cipher = cipher
        self._otp = otp

    async def execute(self, ctx: AuthContext, ip: str) -> OtpSent:
        async with self._uow as uow:
            user = await uow.users.get(ctx.user_id)
            device = await uow.devices.get_for_user(ctx.user_id, ctx.device_id)
        if user is None or device is None:
            raise NotFoundError()
        phone = self._cipher.decrypt(user.phone_ciphertext)
        return await self._otp.send(phone, installation_id=str(device.installation_id), ip=ip)


class DeleteAccount:
    def __init__(self, uow: UnitOfWork, storage: FileStorage, clock: Clock,
                 checker: OtpChecker | None = None) -> None:
        self._uow = uow
        self._storage = storage
        self._clock = clock
        # None — faqat ichki chaqiruvlar (testlar); API har doim OTP bilan chaqiradi
        self._checker = checker

    async def execute(self, ctx: AuthContext, code: str | None = None) -> None:
        if self._checker is not None:
            async with self._uow as uow:
                user = await uow.users.get(ctx.user_id)
            if user is None:
                raise NotFoundError()
            await self._checker.check(user.phone_index, code or "")
        now = self._clock.now()
        async with self._uow as uow:
            await uow.sessions.revoke_all_for_user(ctx.user_id, RevokeReason.ACCOUNT_DELETED, now)
            file_keys = await uow.exports.file_keys_for_user(ctx.user_id)
            file_keys += await uow.receipts.file_keys_for_user(ctx.user_id)
            await uow.users.purge(ctx.user_id)
            await record_audit(uow, self._clock, AuditAction.ACCOUNT_DELETE_REQUESTED,
                               user_id=ctx.user_id, device_id=ctx.device_id)
            await uow.commit()
        for key in file_keys:
            await self._storage.delete(key)
