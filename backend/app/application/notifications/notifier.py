"""Notifier porti implementatsiyasi: ilova ichidagi bildirishnoma + push (BE-401..404).

- In-app yozuv har doim saqlanadi (push yetib bormasa ham user ko'radi), matn user tilida.
- Push navbati (outbox): yozuv `push_status=pending` bilan saqlanadi, darhol yuborishga
  urinadi; muvaffaqiyatsiz bo'lsa `python -m app.jobs push` qayta urinadi (3 martagacha).
- `notifications_enabled = false` — push yuborilmaydi, in-app yoziladi (xavfsizlikdan tashqari).
- Xavfsizlik push matni umumiy: qulflangan ekranda ko'rinadi, unda qurilma nomi yo'q.
- Push xatosi so'rovni (login, refresh) yiqitmaydi — faqat loglanadi.
"""

import asyncio
import logging
from collections.abc import Callable
from uuid import UUID

from app.application.common.interfaces import Clock, PushSender, PushSendResult, Renderer
from app.application.common.uow import UnitOfWork
from app.core.i18n import DEFAULT_LANGUAGE, t
from app.domain.common.ids import uuid7
from app.domain.notifications.entities import (
    DEEP_LINKS,
    MAX_PUSH_ATTEMPTS,
    Notification,
    NotificationType,
    PushScope,
    PushStatus,
)

logger = logging.getLogger("finora.notifications")

PUSH_TIMEOUT_SECONDS = 5.0

_REVOKE_KEYS = {
    "new_sign_in": "notif.security.refresh_reuse",
    "refresh_reuse": "notif.security.refresh_reuse",
    "pin_failures": "notif.security.pin_failures",
}


class AppNotifier:
    def __init__(self, uow_factory: Callable[[], UnitOfWork], push: PushSender | None,
                 clock: Clock) -> None:
        self._uow = uow_factory
        self._push = push
        self._clock = clock

    async def notify(
        self, user_id: UUID, type_: NotificationType, render: Renderer, *,
        dedupe_key: str | None = None, push_render: Renderer | None = None,
        exclude_device_id: UUID | None = None, push_scope: PushScope = PushScope.ACTIVE,
        force_push: bool = False,
    ) -> bool:
        async with self._uow() as uow:
            user = await uow.users.get(user_id)
            if user is None:
                return False
            locale = user.language or DEFAULT_LANGUAGE
            title, body = render(locale)
            p_title, p_body = push_render(locale) if push_render else (title, body)
            wants_push = self._push is not None and (user.notifications_enabled or force_push)
            n = Notification(
                id=uuid7(), user_id=user_id, type=type_, title=title[:128], body=body[:512],
                created_at=self._clock.now(), deep_link=DEEP_LINKS.get(type_),
                dedupe_key=dedupe_key,
                push_status=PushStatus.PENDING if wants_push else PushStatus.NONE,
                push_title=p_title[:128], push_body=p_body[:256],
                exclude_device_id=exclude_device_id, push_scope=push_scope,
            )
            if not await uow.notifications.add(n):
                return False
            await uow.commit()
        if wants_push:
            await self.deliver(n)
        return True

    async def new_sign_in(self, user_id: UUID, exclude_device_id: UUID, device_name: str,
                          city: str | None = None) -> None:
        def render(locale: str) -> tuple[str, str]:
            where = t("notif.security.where", locale, city=city) if city else ""
            return (t("notif.security.new_sign_in.title", locale),
                    t("notif.security.new_sign_in.body", locale, where=where,
                      device=device_name))

        def push_render(locale: str) -> tuple[str, str]:
            return ("Finora: " + t("notif.security.new_sign_in.title", locale),
                    t("notif.security.push_body", locale))

        await self.notify(user_id, NotificationType.SECURITY, render, push_render=push_render,
                          exclude_device_id=exclude_device_id, force_push=True)

    async def sessions_revoked(self, user_id: UUID, reason: str) -> None:
        key = _REVOKE_KEYS.get(reason, "notif.security.refresh_reuse")
        # Sessiyalar allaqachon bekor — shuning uchun token bor barcha qurilmalarga
        await self.notify(
            user_id, NotificationType.SECURITY,
            lambda loc: (t("notif.security.title", loc), t(key, loc)),
            push_scope=PushScope.ALL, force_push=True,
        )

    async def security(self, user_id: UUID, body_key: str, *,
                       exclude_device_id: UUID | None = None, **params: str) -> None:
        await self.notify(
            user_id, NotificationType.SECURITY,
            lambda loc: (t("notif.security.title", loc), t(body_key, loc, **params)),
            push_render=lambda loc: (t("notif.security.title", loc),
                                     t("notif.security.push_body", loc)),
            exclude_device_id=exclude_device_id, force_push=True,
        )

    async def deliver(self, n: Notification) -> None:
        """Push yuborish. Natija: sent / pending (qayta urinish) / failed (3 urinishdan keyin)."""
        async with self._uow() as uow:
            targets = await uow.push_tokens.targets(
                n.user_id, active_only=n.push_scope is PushScope.ACTIVE,
                exclude_device_id=n.exclude_device_id,
            )
        attempts = n.push_attempts + 1
        if self._push is None or not targets:
            status = PushStatus.SENT if self._push is not None else PushStatus.NONE
            await self._set_status(n.id, status, attempts)
            return
        push = self._push
        title, body = n.push_title or n.title, n.push_body or n.body
        try:
            async with asyncio.timeout(PUSH_TIMEOUT_SECONDS):
                results = await asyncio.gather(
                    *(push.send(tg.provider, tg.token, title, body) for tg in targets),
                    return_exceptions=True,
                )
        except TimeoutError:
            logger.warning("push_timeout", extra={"targets": len(targets)})
            results = [PushSendResult.FAILED] * len(targets)
        invalid = [tg.token for tg, r in zip(targets, results, strict=True)
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
        # Hech biri yetib bormagan bo'lsa — qayta urinamiz
        if failed and failed + len(invalid) == len(targets):
            status = PushStatus.FAILED if attempts >= MAX_PUSH_ATTEMPTS else PushStatus.PENDING
        else:
            status = PushStatus.SENT
        await self._set_status(n.id, status, attempts)

    async def _set_status(self, notification_id: UUID, status: PushStatus, attempts: int) -> None:
        async with self._uow() as uow:
            await uow.notifications.set_push_status(notification_id, status.value, attempts)
            await uow.commit()

    async def retry_pending(self, limit: int = 500) -> int:
        async with self._uow() as uow:
            pending = await uow.notifications.pending_push(limit)
        for n in pending:
            await self.deliver(n)
        return len(pending)
