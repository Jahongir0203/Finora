from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.notifications.entities import (
    Notification,
    NotificationType,
    PushProvider,
    PushScope,
    PushStatus,
    PushTarget,
)
from app.infrastructure.db.models import DeviceModel, NotificationModel, SessionModel

N = NotificationModel


def _notification(m: NotificationModel) -> Notification:
    return Notification(
        id=m.id, user_id=m.user_id, type=NotificationType(m.type), title=m.title, body=m.body,
        created_at=m.created_at, deep_link=m.deep_link, read_at=m.read_at,
        deleted_at=m.deleted_at, dedupe_key=m.dedupe_key, push_status=PushStatus(m.push_status),
        push_attempts=m.push_attempts, push_title=m.push_title, push_body=m.push_body,
        exclude_device_id=m.exclude_device_id, push_scope=PushScope(m.push_scope),
    )


class SqlNotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, n: Notification) -> bool:
        m = N(id=n.id, user_id=n.user_id, type=n.type.value, title=n.title, body=n.body,
              deep_link=n.deep_link, created_at=n.created_at, dedupe_key=n.dedupe_key,
              push_status=n.push_status.value, push_attempts=n.push_attempts,
              push_title=n.push_title, push_body=n.push_body,
              exclude_device_id=n.exclude_device_id, push_scope=n.push_scope.value)
        if n.dedupe_key is None:
            self._s.add(m)
            await self._s.flush()
            return True
        try:
            async with self._s.begin_nested():
                self._s.add(m)
                await self._s.flush()
        except IntegrityError:
            return False
        return True

    async def list_for_user(self, user_id: UUID, *, limit: int,
                            after: tuple[datetime, UUID] | None = None) -> list[Notification]:
        stmt = select(N).where(N.user_id == user_id, N.deleted_at.is_(None))
        if after is not None:
            at, last_id = after
            stmt = stmt.where(or_(N.created_at < at, and_(N.created_at == at, N.id < last_id)))
        rows = await self._s.scalars(stmt.order_by(N.created_at.desc(), N.id.desc()).limit(limit))
        return [_notification(m) for m in rows]

    async def unread_count(self, user_id: UUID) -> int:
        n = await self._s.scalar(
            select(func.count()).select_from(N).where(
                N.user_id == user_id, N.read_at.is_(None), N.deleted_at.is_(None))
        )
        return int(n or 0)

    async def mark_read(self, user_id: UUID, notification_id: UUID, at: datetime) -> bool:
        result = await self._s.execute(
            update(N).where(N.id == notification_id, N.user_id == user_id,
                            N.deleted_at.is_(None))
            .values(read_at=func.coalesce(N.read_at, at))
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def mark_all_read(self, user_id: UUID, at: datetime) -> int:
        result = await self._s.execute(
            update(N).where(N.user_id == user_id, N.read_at.is_(None), N.deleted_at.is_(None))
            .values(read_at=at)
        )
        return result.rowcount or 0  # type: ignore[attr-defined]

    async def clear(self, user_id: UUID, at: datetime) -> int:
        result = await self._s.execute(
            update(N).where(N.user_id == user_id, N.deleted_at.is_(None))
            .values(deleted_at=at, read_at=func.coalesce(N.read_at, at))
        )
        return result.rowcount or 0  # type: ignore[attr-defined]

    async def pending_push(self, limit: int) -> list[Notification]:
        rows = await self._s.scalars(
            select(N).where(N.push_status == PushStatus.PENDING.value)
            .order_by(N.created_at).limit(limit)
        )
        return [_notification(m) for m in rows]

    async def set_push_status(self, notification_id: UUID, status: str, attempts: int) -> None:
        await self._s.execute(
            update(N).where(N.id == notification_id)
            .values(push_status=status, push_attempts=attempts)
        )


class SqlPushTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def set(self, user_id: UUID, device_id: UUID, provider: PushProvider | None,
                  token: str | None) -> bool:
        if token is not None:
            # Token boshqa qurilma yozuvida qolgan bo'lsa (qayta o'rnatish) — u yerdan olinadi,
            # aks holda bitta telefon ikki akkaunt bildirishnomasini olishi mumkin
            await self._s.execute(
                update(DeviceModel).where(DeviceModel.push_token == token)
                .values(push_token=None, push_provider=None)
            )
        result = await self._s.execute(
            update(DeviceModel).where(DeviceModel.id == device_id, DeviceModel.user_id == user_id)
            .values(push_token=token, push_provider=provider.value if provider else None)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def targets(self, user_id: UUID, *, active_only: bool,
                      exclude_device_id: UUID | None = None) -> list[PushTarget]:
        stmt = select(DeviceModel).where(DeviceModel.user_id == user_id,
                                         DeviceModel.push_token.is_not(None))
        if exclude_device_id is not None:
            stmt = stmt.where(DeviceModel.id != exclude_device_id)
        if active_only:
            active = select(SessionModel.device_id).where(SessionModel.user_id == user_id,
                                                          SessionModel.revoked_at.is_(None))
            stmt = stmt.where(DeviceModel.id.in_(active))
        rows = await self._s.scalars(stmt)
        return [PushTarget(device_id=m.id, provider=PushProvider(m.push_provider),
                           token=m.push_token) for m in rows
                if m.push_token and m.push_provider]

    async def clear_token(self, token: str) -> None:
        await self._s.execute(
            update(DeviceModel).where(DeviceModel.push_token == token)
            .values(push_token=None, push_provider=None)
        )
