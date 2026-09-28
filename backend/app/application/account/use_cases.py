"""Akkauntni o'chirish (01-umumiy.md, 5; 02-backend.md, 5-bo'lim).

Shaxsiy ma'lumotlar darhol o'chiriladi (30 kunlik talabdan qattiqroq). Zaxiralardan
navbatdagi aylanishda. Audit logda faqat user_id qoladi — shaxsiy ma'lumot yo'q.
"""

from app.application.auth.dto import AuthContext
from app.application.common.audit import record_audit
from app.application.common.interfaces import Clock, FileStorage
from app.application.common.uow import UnitOfWork
from app.domain.audit.entities import AuditAction
from app.domain.auth.entities import RevokeReason


class DeleteAccount:
    def __init__(self, uow: UnitOfWork, storage: FileStorage, clock: Clock) -> None:
        self._uow = uow
        self._storage = storage
        self._clock = clock

    async def execute(self, ctx: AuthContext) -> None:
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
