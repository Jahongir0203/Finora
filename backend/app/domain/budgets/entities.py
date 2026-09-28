from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

from app.domain.common.values import ensure_amount, ensure_name

# O'zbekiston: UTC+5, yozgi vaqt yo'q — oy chegaralari mahalliy vaqt bo'yicha
UZ_TZ = timezone(timedelta(hours=5), "Asia/Tashkent")


@dataclass(slots=True)
class Budget:
    """Kategoriya bo'yicha oylik limit. Sarflangan summa saqlanmaydi — hisoblanadi."""

    id: UUID
    user_id: UUID
    category: str
    monthly_limit: int
    created_at: datetime

    def __post_init__(self) -> None:
        self.category = ensure_name(self.category)
        ensure_amount(self.monthly_limit)


def month_bounds(now: datetime) -> tuple[datetime, datetime]:
    """Joriy oy [boshi, keyingi oy boshi) — UTC'da, mahalliy (UTC+5) oy bo'yicha."""
    local = now.astimezone(UZ_TZ)
    start = local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    nxt = (start.replace(year=start.year + 1, month=1) if start.month == 12
           else start.replace(month=start.month + 1))
    return start.astimezone(UTC), nxt.astimezone(UTC)
