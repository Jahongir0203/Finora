"""Vaqt zonasi va davr chegaralari.

Bazada vaqt har doim UTC. Kun/hafta/oy/yil chegaralari foydalanuvchi vaqt zonasida
hisoblanadi (mijoz `X-Timezone` sarlavhasini yuboradi, standart — Asia/Tashkent).
"""

import calendar
import re
from datetime import UTC, date, datetime, time, timedelta, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TZ_NAME = "Asia/Tashkent"
DEFAULT_TZ = ZoneInfo(DEFAULT_TZ_NAME)

_TZ_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_+\-]*(/[A-Za-z0-9_+\-]+){0,2}$")


def parse_tz(name: str | None) -> ZoneInfo | None:
    """IANA nomi -> ZoneInfo. Noto'g'ri yoki noma'lum nom — None (fayl yo'li emas)."""
    if not name or len(name) > 64 or not _TZ_NAME.fullmatch(name):
        return None
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return None


def tz_or_default(name: str | None) -> ZoneInfo:
    return parse_tz(name) or DEFAULT_TZ


def local_midnight(d: date, tz: tzinfo) -> datetime:
    return datetime.combine(d, time.min, tzinfo=tz).astimezone(UTC)


def day_bounds(d: date, tz: tzinfo) -> tuple[datetime, datetime]:
    return local_midnight(d, tz), local_midnight(d + timedelta(days=1), tz)


def week_start(d: date) -> date:
    """ISO hafta — dushanbadan."""
    return d - timedelta(days=d.weekday())


def month_start(d: date) -> date:
    return d.replace(day=1)


def add_months(d: date, months: int, anchor_day: int | None = None) -> date:
    """Oy qo'shadi; kun oy oxiridan oshsa oxirgi kunga tushadi (31 -> 30/28).
    anchor_day — asl kun (keyingi oylarda yana 31 ga qaytish uchun)."""
    total = d.year * 12 + (d.month - 1) + months
    year, month = divmod(total, 12)
    day = anchor_day or d.day
    return date(year, month + 1, min(day, calendar.monthrange(year, month + 1)[1]))


def month_bounds(now: datetime, tz: tzinfo = DEFAULT_TZ) -> tuple[datetime, datetime]:
    """Joriy oy [boshi, keyingi oy boshi) — UTC'da, mahalliy oy bo'yicha."""
    start = month_start(now.astimezone(tz).date())
    return local_midnight(start, tz), local_midnight(add_months(start, 1), tz)


def month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def parse_month(value: str) -> date:
    m = re.fullmatch(r"(\d{4})-(\d{2})", value)
    if not m or not 1 <= int(m.group(2)) <= 12:
        raise ValueError("month YYYY-MM formatida bo'lishi kerak")
    return date(int(m.group(1)), int(m.group(2)), 1)
