"""Bildirishnomalar (BE-401..404).

In-app yozuv har doim saqlanadi; push — navbat (outbox) orqali: `push_status=pending` yozuvlar
darhol yuborishga urinadi, muvaffaqiyatsiz bo'lsa scheduler qayta urinadi.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

MAX_PUSH_ATTEMPTS = 3


class NotificationType(StrEnum):
    PAYMENT_DUE = "payment_due"
    INCOME = "income"
    BUDGET_EXCEEDED = "budget_exceeded"
    WEEKLY_REPORT = "weekly_report"
    GOAL_MILESTONE = "goal_milestone"
    SECURITY = "security"


# Eski nom
NotificationKind = NotificationType

DEEP_LINKS = {
    NotificationType.PAYMENT_DUE: "/reminders",
    NotificationType.INCOME: "/activity",
    NotificationType.BUDGET_EXCEEDED: "/budgets",
    NotificationType.WEEKLY_REPORT: "/stats",
    NotificationType.GOAL_MILESTONE: "/budgets",
    NotificationType.SECURITY: "/profile",
}


class PushStatus(StrEnum):
    NONE = "none"  # push kerak emas (sozlama o'chiq yoki qurilma yo'q)
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class PushScope(StrEnum):
    ACTIVE = "active"  # faqat faol sessiyasi bor qurilmalar
    ALL = "all"  # token bor barcha qurilmalar ("sessiyalar yopildi" xabari uchun)


class PushProvider(StrEnum):
    FCM = "fcm"
    APNS = "apns"


@dataclass(slots=True)
class Notification:
    """Ilova ichidagi bildirishnoma. Matnda telefon, token bo'lmaydi."""

    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    created_at: datetime
    deep_link: str | None = None
    read_at: datetime | None = None
    deleted_at: datetime | None = None
    # Takroriy yuborilmasligi uchun: "payment_due:<id>:2026-09-30:d0" (user_id bilan unique)
    dedupe_key: str | None = None
    push_status: PushStatus = PushStatus.NONE
    push_attempts: int = 0
    # Qulflangan ekranda ko'rinadigan matn (xavfsizlik bildirishnomasida qurilma nomi yo'q)
    push_title: str | None = None
    push_body: str | None = None
    # Push faqat shu qurilmalarga emas (masalan, yangi kirgan qurilmaning o'ziga yuborilmaydi)
    exclude_device_id: UUID | None = None
    push_scope: PushScope = PushScope.ACTIVE

    @property
    def kind(self) -> NotificationType:
        return self.type


@dataclass(frozen=True, slots=True)
class PushTarget:
    device_id: UUID
    provider: PushProvider
    token: str
