"""Eksport (BE-601, BE-602).

- Preview — sinxron; yaratish — asinxron job (status: pending → ready | failed).
- Havola HMAC bilan imzolangan (5 daqiqa, har so'rovda yangisi) va bir martalik;
  fayl yuklab olingandan keyin yoki 24 soatdan keyin o'chiriladi.
- CSV/Excel formula injection himoyasi (`=`, `+`, `-`, `@` oldiga `'`).
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta, tzinfo
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.audit import record_audit
from app.application.common.interfaces import Clock, FileStorage, ReportRenderer, UrlSigner
from app.application.common.rate_limit import HOUR, Limit, RateLimiter
from app.application.common.uow import UnitOfWork
from app.application.exports.report import (
    CategoryLine,
    ExportReport,
    ReportLabels,
    ReportRow,
)
from app.application.finance.catalog import CategoryCatalog
from app.application.stats.use_cases import percentages
from app.core.config import Settings
from app.core.i18n import t
from app.domain.audit.entities import AuditAction
from app.domain.common.errors import NotFoundError, ValidationFailedError
from app.domain.common.ids import uuid7
from app.domain.common.time import local_midnight, tz_or_default
from app.domain.exports.entities import (
    CONTENT_TYPES,
    Export,
    ExportFormat,
    ExportPeriod,
    ExportStatus,
    file_name,
    period_range,
    range_label,
)
from app.domain.transactions.entities import Transaction, TransactionType
from app.domain.transactions.repository import TransactionFilter

logger = logging.getLogger("finora.exports")

MAX_EXPORT_ROWS = 100_000
SIGNED_URL_TTL_SECONDS = 5 * 60


def export_resource(export_id: UUID) -> str:
    return f"export:{export_id}"


@dataclass(frozen=True, slots=True)
class Summary:
    start: date
    end: date
    count: int
    income: int
    expenses: int
    rows: list[Transaction]

    @property
    def net(self) -> int:
        return self.income - self.expenses


async def _summary(uow: UnitOfWork, user_id: UUID, start: date, end: date,
                   include: list[TransactionType], tz: tzinfo) -> Summary:
    rows = await uow.transactions.list_for_user(
        user_id, TransactionFilter(types=tuple(include), since=local_midnight(start, tz),
                                   until=local_midnight(end + timedelta(days=1), tz)),
        limit=MAX_EXPORT_ROWS)
    income = sum(r.amount for r in rows if r.type is TransactionType.INCOME)
    expenses = sum(r.amount for r in rows if r.type is TransactionType.EXPENSE)
    return Summary(start, end, len(rows), income, expenses, rows)


def _labels(locale: str) -> ReportLabels:
    return ReportLabels(**{
        f: t(f"export.{f.replace('col_', 'col.')}", locale)
        for f in ReportLabels.__dataclass_fields__
    })


class ExportService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork], storage: FileStorage,
                 signer: UrlSigner, limiter: RateLimiter, clock: Clock, settings: Settings,
                 renderers: dict[ExportFormat, ReportRenderer]) -> None:
        self._uow = uow_factory
        self._storage = storage
        self._signer = signer
        self._limiter = limiter
        self._clock = clock
        self._s = settings
        self._renderers = renderers

    @staticmethod
    def _check_include(include: list[TransactionType]) -> list[TransactionType]:
        if not include:
            raise ValidationFailedError("include bo'sh", fields=["include"])
        return list(dict.fromkeys(include))

    async def preview(self, ctx: AuthContext, period: ExportPeriod,
                      include: list[TransactionType], fmt: ExportFormat,
                      tz: tzinfo) -> dict[str, Any]:
        include = self._check_include(include)
        today = self._clock.now().astimezone(tz).date()
        r = period_range(period, today)
        async with self._uow() as uow:
            s = await _summary(uow, ctx.user_id, r.start, min(r.end, today), include, tz)
        return {"range_label": range_label(r), "from": r.start.isoformat(),
                "to": r.end.isoformat(), "count": s.count, "income": s.income,
                "expenses": s.expenses, "net": s.net, "file_name": file_name(period, r, fmt)}

    async def create(self, ctx: AuthContext, period: ExportPeriod,
                     include: list[TransactionType], fmt: ExportFormat,
                     tz_name: str) -> Export:
        include = self._check_include(include)
        await self._limiter.hit("exports", str(ctx.user_id),
                                [Limit("hour", self._s.exports_per_hour, HOUR)])
        now = self._clock.now()
        tz = tz_or_default(tz_name)
        r = period_range(period, now.astimezone(tz).date())
        async with self._uow() as uow:
            user = await uow.users.get(ctx.user_id)
            export = Export(
                id=uuid7(), user_id=ctx.user_id, period=period, format=fmt, include=include,
                range_start=r.start, range_end=r.end, file_name=file_name(period, r, fmt),
                created_at=now, expires_at=now + timedelta(seconds=self._s.export_ttl_seconds),
                language=user.language if user else "uz-Latn", timezone=str(tz),
            )
            await uow.exports.add(export)
            await record_audit(uow, self._clock, AuditAction.EXPORT_CREATED,
                               user_id=ctx.user_id, device_id=ctx.device_id,
                               period=period.value, format=fmt.value)
            await uow.commit()
        return export

    async def process(self, export_id: UUID) -> None:
        """Job: faylni yaratadi. Xato bo'lsa status=failed (UI "Export failed")."""
        async with self._uow() as uow:
            export = await uow.exports.get(export_id)
            if export is None or export.status is not ExportStatus.PENDING:
                return
            try:
                tz = tz_or_default(export.timezone)
                today = self._clock.now().astimezone(tz).date()
                s = await _summary(uow, export.user_id, export.range_start,
                                   min(export.range_end, today), export.include, tz)
                catalog = await CategoryCatalog.load(uow, export.user_id, export.language)
                report = self._build(export, s, catalog, tz)
                rendered = self._renderers[export.format].render(report)
                key = f"exports/{export.user_id}/{export.id}.{export.format.value}"
                await self._storage.put(key, rendered.data, rendered.content_type)
                now = self._clock.now()
                export.status, export.file_key, export.ready_at = ExportStatus.READY, key, now
                export.row_count = s.count
                export.expires_at = now + timedelta(seconds=self._s.export_ttl_seconds)
            except Exception:
                logger.exception("export_failed")
                export.status, export.error_code = ExportStatus.FAILED, "render_failed"
            await uow.exports.update(export)
            await uow.commit()

    def _build(self, export: Export, s: Summary, catalog: CategoryCatalog,
               tz: tzinfo) -> ExportReport:
        loc = export.language
        by_cat: dict[str, int] = {}
        for r in s.rows:
            if r.type is TransactionType.EXPENSE:
                by_cat[r.category_id] = by_cat.get(r.category_id, 0) + r.amount
        ordered = sorted(by_cat.items(), key=lambda kv: -kv[1])
        pcts = percentages([a for _, a in ordered])
        rows = [ReportRow(
            date=r.occurred_at.astimezone(tz).date().isoformat(),
            type=t(f"type.{r.type.value}", loc), category=catalog.name(r.category_id),
            title=r.title or "", amount=r.signed_amount, note=r.note or "",
        ) for r in s.rows]
        return ExportReport(
            labels=_labels(loc),
            range_label=range_label(period_range(export.period, export.range_start)),
            income=s.income, expenses=s.expenses, net=s.net,
            categories=[CategoryLine(catalog.name(c), a, p)
                        for (c, a), p in zip(ordered, pcts, strict=True)],
            rows=rows,
        )

    async def status(self, ctx: AuthContext, export_id: UUID) -> tuple[Export, str | None,
                                                                       int | None]:
        """(export, imzo, imzo muddati). Imzo faqat yuklab olish mumkin bo'lsa."""
        async with self._uow() as uow:
            export = await uow.exports.get_for_user(ctx.user_id, export_id)
        if export is None:
            raise NotFoundError()
        now = self._clock.now()
        if not export.is_downloadable(now):
            return export, None, None
        exp = int(now.timestamp()) + SIGNED_URL_TTL_SECONDS
        return export, self._signer.sign(export_resource(export.id), exp), exp

    async def download(self, export_id: UUID, expires_at: int,
                       signature: str) -> tuple[bytes, str, str]:
        """Imzo — egalik isboti. Bir martalik: ikkinchi urinish 404."""
        now = self._clock.now()
        if not self._signer.verify(export_resource(export_id), expires_at, signature,
                                   int(now.timestamp())):
            raise NotFoundError()
        async with self._uow() as uow:
            export = await uow.exports.get(export_id)
            if export is None or not export.is_downloadable(now) or export.file_key is None:
                raise NotFoundError()
            if not await uow.exports.mark_downloaded(export.id, now):
                raise NotFoundError()
            data = await self._storage.get(export.file_key)
            if data is None:
                raise NotFoundError()
            await record_audit(uow, self._clock, AuditAction.EXPORT_DOWNLOADED,
                               user_id=export.user_id)
            await uow.commit()
        await self._storage.delete(export.file_key)
        return data, CONTENT_TYPES[export.format], export.file_name

    async def process_stale(self, older_than_seconds: int = 900) -> int:
        """Job: fon vazifasi uzilib qolgan pending eksportlarni qayta ishlaydi."""
        cutoff = self._clock.now() - timedelta(seconds=older_than_seconds)
        async with self._uow() as uow:
            pending = await uow.exports.pending(cutoff)
        for e in pending:
            await self.process(e.id)
        return len(pending)

    async def purge_expired(self) -> int:
        """Cron/worker chaqiradi: muddati o'tgan yoki yuklab olingan eksportlarni o'chiradi."""
        async with self._uow() as uow:
            expired = await uow.exports.list_expired(self._clock.now())
            for e in expired:
                if e.file_key:
                    await self._storage.delete(e.file_key)
                await uow.exports.delete(e.id)
            await uow.commit()
        return len(expired)


def export_to_dict(e: Export, download_url: str | None) -> dict[str, Any]:
    return {"id": str(e.id), "status": e.status.value, "file_name": e.file_name,
            "format": e.format.value, "period": e.period.value,
            "download_url": download_url, "error_code": e.error_code,
            "row_count": e.row_count, "expires_at": e.expires_at.isoformat()}


