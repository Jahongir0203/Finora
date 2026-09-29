"""AI tavsiyalari (BE-901, BE-902). Qoidaga asoslangan detektorlar natijasi."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class InsightKind(StrEnum):
    OVERSPEND = "overspend"  # kategoriya 3 oylik o'rtachadan > 20% yuqori
    DISCOUNT_DAYS = "discount_days"  # groceries: ko'p mayda xarid
    SUBSCRIPTIONS = "subscriptions"  # takroriy obunalar
    AUTOSAVE = "autosave"  # kirim bor, goal auto-save yo'q


class InsightAction(StrEnum):
    SET_BUDGET = "set_budget"
    REMIND_ME = "remind_me"
    REVIEW = "review"
    TURN_ON_AUTOSAVE = "turn_on_autosave"


class InsightStatus(StrEnum):
    ACTIVE = "active"
    DISMISSED = "dismissed"
    REVIEWED = "reviewed"
    DONE = "done"


@dataclass(slots=True)
class Insight:
    id: UUID
    user_id: UUID
    kind: InsightKind
    action: InsightAction
    icon: str
    saving: int
    # Lokalizatsiya qilinadigan matn parametrlari (summa, kategoriya id, foiz)
    params: dict[str, Any]
    # Bitta davr uchun bitta tavsiya: "overspend:food:2026-09"
    dedupe_key: str
    created_at: datetime
    updated_at: datetime
    category_id: str | None = None
    status: InsightStatus = InsightStatus.ACTIVE
    extra: dict[str, Any] = field(default_factory=dict)
