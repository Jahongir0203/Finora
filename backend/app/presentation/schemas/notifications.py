from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, StringConstraints

from app.domain.auth.entities import Platform
from app.domain.notifications.entities import NotificationType, PushProvider
from app.presentation.schemas.common import StrictModel

PushToken = Annotated[str, StringConstraints(min_length=16, max_length=512,
                                             pattern=r"^[A-Za-z0-9_\-:.]+$")]


class PushTokenIn(StrictModel):
    token: PushToken
    platform: Platform
    # Flutter firebase_messaging iOS'da ham FCM token beradi — standart fcm
    provider: PushProvider = PushProvider.FCM


class NotificationOut(BaseModel):
    id: UUID
    type: NotificationType
    title: str
    body: str
    created_at: datetime
    read: bool
    deep_link: str | None


class NotificationPageOut(BaseModel):
    items: list[NotificationOut]
    next_cursor: str | None
    unread: int


class CountOut(BaseModel):
    count: int
