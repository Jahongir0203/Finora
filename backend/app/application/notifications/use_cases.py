from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.interfaces import Clock
from app.application.common.pagination import Page, clamp_limit, decode_cursor, encode_cursor
from app.application.common.uow import UnitOfWork
from app.domain.common.errors import NotFoundError, ValidationFailedError
from app.domain.notifications.entities import Notification, PushProvider

MAX_PUSH_TOKEN_LENGTH = 512


class NotificationService:
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    async def register_push_token(self, ctx: AuthContext, provider: PushProvider,
                                  token: str) -> None:
        """Token faqat so'rov yuborayotgan (joriy) qurilmaga yoziladi — boshqasiga emas."""
        token = token.strip()
        if not token or len(token) > MAX_PUSH_TOKEN_LENGTH or not token.isprintable():
            raise ValidationFailedError("Push token noto'g'ri", fields=["token"])
        async with self._uow as uow:
            await uow.push_tokens.set(ctx.user_id, ctx.device_id, provider, token)
            await uow.commit()

    async def remove_push_token(self, ctx: AuthContext) -> None:
        async with self._uow as uow:
            await uow.push_tokens.set(ctx.user_id, ctx.device_id, None, None)
            await uow.commit()

    async def list(self, ctx: AuthContext, cursor: str | None,
                   limit: int | None) -> tuple[Page[Notification], int]:
        size = clamp_limit(limit)
        after = decode_cursor(cursor)
        async with self._uow as uow:
            rows = await uow.notifications.list_for_user(
                ctx.user_id, limit=size + 1, after=(after.at, after.id) if after else None)
            unread = await uow.notifications.unread_count(ctx.user_id)
        items = rows[:size]
        nxt = encode_cursor(items[-1].created_at, items[-1].id) if len(rows) > size else None
        return Page(items, nxt), unread

    async def mark_read(self, ctx: AuthContext, notification_id: UUID) -> None:
        async with self._uow as uow:
            if not await uow.notifications.mark_read(ctx.user_id, notification_id,
                                                     self._clock.now()):
                raise NotFoundError()
            await uow.commit()

    async def mark_all_read(self, ctx: AuthContext) -> int:
        async with self._uow as uow:
            n = await uow.notifications.mark_all_read(ctx.user_id, self._clock.now())
            await uow.commit()
        return n

    async def delete(self, ctx: AuthContext, notification_id: UUID) -> None:
        async with self._uow as uow:
            if not await uow.notifications.delete(ctx.user_id, notification_id,
                                                  self._clock.now()):
                raise NotFoundError()
            await uow.commit()

    async def clear(self, ctx: AuthContext) -> int:
        async with self._uow as uow:
            n = await uow.notifications.clear(ctx.user_id, self._clock.now())
            await uow.commit()
        return n
