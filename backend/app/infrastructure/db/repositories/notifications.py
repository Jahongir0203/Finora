from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.notifications.entities import (
    Notification,
    NotificationKind,
    PushProvider,
    PushTarget,
)
from app.infrastructure.db.models import DeviceModel, NotificationModel, SessionModel


class SqlNotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, n: Notification) -> None:
        self._s.add(NotificationModel(id=n.id, user_id=n.user_id, kind=n.kind.value,
                                      title=n.title, body=n.body, created_at=n.created_at))
        await self._s.flush()

    async def list_for_user(self, user_id: UUID, limit: int = 50) -> list[Notification]:
        rows = await self._s.scalars(
            select(NotificationModel).where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.id.desc()).limit(limit)
        )
        return [Notification(id=m.id, user_id=m.user_id, kind=NotificationKind(m.kind),
                             title=m.title, body=m.body, created_at=m.created_at,
                             read_at=m.read_at) for m in rows]

    async def mark_read(self, user_id: UUID, notification_id: UUID, at: datetime) -> bool:
        result = await self._s.execute(
            update(NotificationModel)
            .where(NotificationModel.id == notification_id, NotificationModel.user_id == user_id)
            .values(read_at=at)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]


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
