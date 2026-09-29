from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class AuditAction(StrEnum):
    LOGIN = "login"
    NEW_DEVICE = "new_device"
    LOGOUT = "logout"
    LOGOUT_ALL = "logout_all"
    REFRESH_REUSE = "refresh_reuse"
    PIN_RESET = "pin_reset"
    PIN_FAILURES = "pin_failures"
    ACCOUNT_DELETE_REQUESTED = "account_delete_requested"
    EXPORT_CREATED = "export_created"
    EXPORT_DOWNLOADED = "export_downloaded"
    TELEGRAM_LINKED = "telegram_linked"


@dataclass(slots=True)
class AuditEvent:
    """Audit yozuvi — faqat qo'shiladi (append-only), 1 yil saqlanadi.

    meta'ga shaxsiy ma'lumot (telefon, summa, token) yozilmaydi.
    """

    id: UUID
    user_id: UUID | None
    action: AuditAction
    created_at: datetime
    device_id: UUID | None = None
    ip: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
