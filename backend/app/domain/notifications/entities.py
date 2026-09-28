from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class NotificationKind(StrEnum):
    NEW_SIGN_IN = "new_sign_in"
    SESSIONS_REVOKED = "sessions_revoked"


class PushProvider(StrEnum):
    FCM = "fcm"
    APNS = "apns"


@dataclass(slots=True)
class Notification:
    """Ilova ichidagi bildirishnoma. Matnda telefon, summa, token bo'lmaydi."""

    id: UUID
    user_id: UUID
    kind: NotificationKind
    title: str
    body: str
    created_at: datetime
    read_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class PushTarget:
    device_id: UUID
    provider: PushProvider
    token: str
