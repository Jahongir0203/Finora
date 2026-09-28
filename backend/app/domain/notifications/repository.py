from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.notifications.entities import Notification, PushProvider, PushTarget


class NotificationRepository(Protocol):
    async def add(self, notification: Notification) -> None: ...
    async def list_for_user(self, user_id: UUID, limit: int = 50) -> list[Notification]: ...
    async def mark_read(self, user_id: UUID, notification_id: UUID, at: datetime) -> bool: ...


class PushTokenRepository(Protocol):
    """Push token qurilmaga bog'langan (devices jadvali). Egalik user_id bilan tekshiriladi."""

    async def set(self, user_id: UUID, device_id: UUID, provider: PushProvider | None,
                  token: str | None) -> bool: ...
    async def targets(self, user_id: UUID, *, active_only: bool,
                      exclude_device_id: UUID | None = None) -> list[PushTarget]: ...
    async def clear_token(self, token: str) -> None:
        """Provayder token yaroqsiz desa (UNREGISTERED / 410) — o'chiriladi."""
        ...
