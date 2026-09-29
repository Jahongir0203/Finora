"""Eksport (BE-601, BE-602). Fayl 24 soat saqlanadi, yuklab olish havolasi bir martalik."""

import calendar
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import StrEnum
from uuid import UUID

from app.domain.common.time import month_start, week_start
from app.domain.transactions.entities import TransactionType


class ExportPeriod(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ExportFormat(StrEnum):
    PDF = "pdf"
    XLSX = "xlsx"
    CSV = "csv"


class ExportStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


CONTENT_TYPES = {
    ExportFormat.PDF: "application/pdf",
    ExportFormat.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ExportFormat.CSV: "text/csv; charset=utf-8",
}


@dataclass(frozen=True, slots=True)
class PeriodRange:
    start: date  # kiradi
    end: date  # kiradi (bugun)
    part: str  # fayl nomi qismi: 28sep2026, w39_2026, sep2026, 2026


def period_range(period: ExportPeriod, today: date) -> PeriodRange:
    """Daily — bugun; Weekly — joriy ISO hafta; Monthly — joriy oy; Yearly — yil boshidan."""
    mon = calendar.month_abbr[today.month].lower()
    if period is ExportPeriod.DAILY:
        return PeriodRange(today, today, f"{today.day}{mon}{today.year}")
    if period is ExportPeriod.WEEKLY:
        iso = today.isocalendar()
        start = week_start(today)
        return PeriodRange(start, start + timedelta(days=6), f"w{iso.week}_{iso.year}")
    if period is ExportPeriod.MONTHLY:
        start = month_start(today)
        last = calendar.monthrange(today.year, today.month)[1]
        return PeriodRange(start, start.replace(day=last), f"{mon}{today.year}")
    return PeriodRange(date(today.year, 1, 1), today, str(today.year))


def range_label(r: PeriodRange) -> str:
    if r.start == r.end:
        return f"{r.start.day} {calendar.month_abbr[r.start.month]} {r.start.year}"
    if r.start.year == r.end.year:
        return (f"{r.start.day} {calendar.month_abbr[r.start.month]} - "
                f"{r.end.day} {calendar.month_abbr[r.end.month]} {r.end.year}")
    return f"{r.start.isoformat()} - {r.end.isoformat()}"


def file_name(period: ExportPeriod, r: PeriodRange, fmt: ExportFormat) -> str:
    return f"finora_{period.value}_{r.part}.{fmt.value}"


@dataclass(slots=True)
class Export:
    id: UUID
    user_id: UUID
    period: ExportPeriod
    format: ExportFormat
    include: list[TransactionType]
    range_start: date
    range_end: date
    file_name: str
    created_at: datetime
    expires_at: datetime
    status: ExportStatus = ExportStatus.PENDING
    file_key: str | None = None
    error_code: str | None = None
    row_count: int = 0
    ready_at: datetime | None = None
    downloaded_at: datetime | None = None
    # Hisobot tili (yaratilgan paytdagi user.language)
    language: str = "uz-Latn"
    timezone: str = "Asia/Tashkent"
    meta: dict[str, str] = field(default_factory=dict)

    def is_downloadable(self, now: datetime) -> bool:
        return (self.status is ExportStatus.READY and self.downloaded_at is None
                and now < self.expires_at)
