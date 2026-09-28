from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, StringConstraints

from app.domain.notifications.entities import NotificationKind, PushProvider
from app.presentation.schemas.common import StrictModel

PushToken = Annotated[str, StringConstraints(min_length=16, max_length=512,
                                             pattern=r"^[A-Za-z0-9_\-:.]+$")]


class PushTokenIn(StrictModel):
    provider: PushProvider
    token: PushToken


class NotificationOut(BaseModel):
    id: UUID
    kind: NotificationKind
    title: str
    body: str
    created_at: datetime
    read_at: datetime | None
