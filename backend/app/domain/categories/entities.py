"""Kategoriyalar (BE-1501).

- Tizim kategoriyalari kodda (seed), id — barqaror slug ("groceries"). Nomi lokalizatsiya qilinadi.
- User kategoriyalari bazada, id — UUIDv7 (satr ko'rinishida).
- Limit va nom override har ikkala tur uchun `category_prefs` jadvalida (tizim kategoriyasining
  o'zi o'zgarmaydi).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.common.errors import ValidationFailedError
from app.domain.common.values import ensure_amount


class CategoryType(StrEnum):
    EXPENSE = "expense"
    INCOME = "income"


# Dizayndagi ruxsat etilgan ikon va ranglar (PROFILE_SETTINGS.md, 5.1)
ALLOWED_ICONS = frozenset({
    "shopping-cart", "utensils", "coffee", "car", "bus", "receipt", "heart-pulse", "dumbbell",
    "shopping-bag", "house", "repeat", "plane", "graduation-cap", "gift", "baby", "paw-print",
    "smartphone", "briefcase",
})
ALLOWED_COLORS = frozenset({
    "#10B981", "#14B8A6", "#0EA5E9", "#3B82F6", "#6366F1", "#8B5CF6", "#EC4899", "#EF4444",
    "#F59E0B", "#84CC16",
})
MAX_CATEGORY_NAME = 32


@dataclass(frozen=True, slots=True)
class SystemCategory:
    id: str
    icon: str
    color: str
    type: CategoryType


SYSTEM_CATEGORIES: dict[str, SystemCategory] = {c.id: c for c in (
    SystemCategory("groceries", "shopping-cart", "#10B981", CategoryType.EXPENSE),
    SystemCategory("food", "utensils", "#F59E0B", CategoryType.EXPENSE),
    SystemCategory("transport", "car", "#3B82F6", CategoryType.EXPENSE),
    SystemCategory("bills", "receipt", "#8B5CF6", CategoryType.EXPENSE),
    SystemCategory("health", "heart-pulse", "#EF4444", CategoryType.EXPENSE),
    SystemCategory("shopping", "shopping-bag", "#EC4899", CategoryType.EXPENSE),
    SystemCategory("housing", "house", "#14B8A6", CategoryType.EXPENSE),
    SystemCategory("subs", "repeat", "#6366F1", CategoryType.EXPENSE),
    SystemCategory("salary", "briefcase", "#10B981", CategoryType.INCOME),
    SystemCategory("transfer", "arrow-left-right", "#0EA5E9", CategoryType.INCOME),
)}
TRANSFER_CATEGORY_ID = "transfer"


def ensure_category_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValidationFailedError(fields=["name"], code="category_name_required")
    if len(value) > MAX_CATEGORY_NAME:
        raise ValidationFailedError(f"Nom {MAX_CATEGORY_NAME} belgidan oshmasin", fields=["name"])
    return value


@dataclass(slots=True)
class UserCategory:
    id: UUID
    user_id: UUID
    name: str
    icon: str
    color: str
    type: CategoryType
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.name = ensure_category_name(self.name)
        if self.icon not in ALLOWED_ICONS:
            raise ValidationFailedError("Ikon ruxsat etilgan ro'yxatda emas", fields=["icon"])
        self.color = self.color.upper()
        if self.color not in ALLOWED_COLORS:
            raise ValidationFailedError("Rang ruxsat etilgan ro'yxatda emas", fields=["color"])


@dataclass(slots=True)
class CategoryPref:
    user_id: UUID
    category_id: str
    updated_at: datetime
    monthly_limit: int | None = None
    name_override: str | None = None

    def __post_init__(self) -> None:
        if self.monthly_limit is not None:
            ensure_amount(self.monthly_limit)
        if self.name_override is not None:
            self.name_override = ensure_category_name(self.name_override)


@dataclass(frozen=True, slots=True)
class Category:
    """Mijozga ko'rsatiladigan birlashgan ko'rinish."""

    id: str
    name: str
    icon: str
    color: str
    type: CategoryType
    is_system: bool
    monthly_limit: int | None
