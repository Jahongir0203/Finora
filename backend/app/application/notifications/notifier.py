"""Notifier porti implementatsiyasi: ilova ichidagi bildirishnoma + push (02-backend.md, 2-bo'lim).

- Ilova ichidagi yozuv har doim saqlanadi (push yetib bormasa ham user ko'radi).
- Push matni umumiy: qulflangan ekranda ko'rinadi, shuning uchun unda qurilma nomi yo'q.
- Push xatosi so'rovni (login, refresh) yiqitmaydi — faqat loglanadi.
"""

import asyncio
import logging
from collections.abc import Callable
from uuid import UUID

from app.application.common.interfaces import Clock, PushSender, PushSendResult
from app.application.common.uow import UnitOfWork
from app.domain.common.ids import uuid7
from app.domain.notifications.entities import Notification, NotificationKind, PushTarget

logger = logging.getLogger("finora.notifications")

PUSH_TIMEOUT_SECONDS = 5.0

_REVOKE_TEXT = {
    "new_sign_in": "Xavfsizlik uchun barcha sessiyalar yopildi. Qayta kiring.",
    "pin_failures": "Ko'p marta noto'g'ri PIN kiritildi. Qurilma sessiyasi yopildi.",
}


class AppNotifier:
    def __init__(self, uow_factory: Callable[[], UnitOfWork], push: PushSender | None,
                 clock: Clock) -> None:
        self._uow = uow_factory
        self._push = push
        self._clock = clock

    async def new_sign_in(self, user_id: UUID, exclude_device_id: UUID, device_name: str) -> None:
        targets = await self._store(
            user_id, NotificationKind.NEW_SIGN_IN, "Yangi kirish",
            f"Hisobingizga yangi qurilmadan kirildi: {device_name}. Bu siz bo'lmasangiz, "
            "Profil → Qurilmalar bo'limida barcha qurilmalardan chiqing.",
            active_only=True, exclude_device_id=exclude_device_id,
        )
        await self._send_all(targets, "Finora: yangi kirish",
                             "Hisobingizga yangi qurilmadan kirildi. Ilovani oching.")

    async def sessions_revoked(self, user_id: UUID, reason: str) -> None:
        body = _REVOKE_TEXT.get(reason, "Sessiya yopildi. Qayta kiring.")
        # Sessiyalar allaqachon bekor — shuning uchun token bor barcha qurilmalarga
        targets = await self._store(user_id, NotificationKind.SESSIONS_REVOKED,
                                    "Xavfsizlik ogohlantirishi", body, active_only=False)
        await self._send_all(targets, "Finora: xavfsizlik", body)

    async def _store(self, user_id: UUID, kind: NotificationKind, title: str, body: str, *,
                     active_only: bool, exclude_device_id: UUID | None = None) -> list[PushTarget]:
        async with self._uow() as uow:
            await uow.notifications.add(Notification(
                id=uuid7(), user_id=user_id, kind=kind, title=title, body=body[:512],
                created_at=self._clock.now(),
            ))
            targets = await uow.push_tokens.targets(user_id, active_only=active_only,
                                                    exclude_device_id=exclude_device_id)
            await uow.commit()
        return targets

    async def _send_all(self, targets: list[PushTarget], title: str, body: str) -> None:
        if self._push is None or not targets:
            return
        push = self._push
        try:
            async with asyncio.timeout(PUSH_TIMEOUT_SECONDS):
                results = await asyncio.gather(
                    *(push.send(t.provider, t.token, title, body) for t in targets),
                    return_exceptions=True,
                )
        except TimeoutError:
            logger.warning("push_timeout", extra={"targets": len(targets)})
            return
        invalid = [t.token for t, r in zip(targets, results, strict=True)
                   if r is PushSendResult.INVALID_TOKEN]
        failed = sum(1 for r in results if isinstance(r, BaseException)
                     or r is PushSendResult.FAILED)
        if failed:
            logger.warning("push_failed", extra={"failed": failed, "targets": len(targets)})
        if invalid:
            async with self._uow() as uow:
                for token in invalid:
                    await uow.push_tokens.clear_token(token)
                await uow.commit()
