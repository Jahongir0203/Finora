"""Eksport: fayl 24 soat saqlanadi, yuklab olish havolasi bir martalik."""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.application.auth.dto import AuthContext
from app.application.common.audit import record_audit
from app.application.common.interfaces import Clock, FileStorage, SecretHasher
from app.application.common.rate_limit import HOUR, Limit, RateLimiter
from app.application.common.uow import UnitOfWork
from app.application.exports.csv_safe import render_csv
from app.core.config import Settings
from app.domain.audit.entities import AuditAction
from app.domain.common.errors import NotFoundError
from app.domain.common.ids import uuid7
from app.domain.exports.entities import Export

MAX_EXPORT_ROWS = 100_000


@dataclass(frozen=True, slots=True)
class ExportCreated:
    download_token: str
    expires_at: datetime


class ExportService:
    def __init__(self, uow: UnitOfWork, storage: FileStorage, hasher: SecretHasher,
                 limiter: RateLimiter, clock: Clock, settings: Settings) -> None:
        self._uow = uow
        self._storage = storage
        self._hasher = hasher
        self._limiter = limiter
        self._clock = clock
        self._s = settings

    async def create(self, ctx: AuthContext, since: datetime | None,
                     until: datetime | None) -> ExportCreated:
        await self._limiter.hit("exports", str(ctx.user_id),
                                [Limit("hour", self._s.exports_per_hour, HOUR)])
        now = self._clock.now()
        async with self._uow as uow:
            txs = await uow.transactions.list_for_user(
                ctx.user_id, since=since, until=until, limit=MAX_EXPORT_ROWS
            )
            data = render_csv(
                ["date", "kind", "category", "amount", "note"],
                ([t.occurred_at.date().isoformat(), t.kind.value, t.category, t.amount, t.note]
                 for t in txs),
            )
            export_id = uuid7()
            file_key = f"exports/{ctx.user_id}/{export_id}.csv"
            await self._storage.put(file_key, data, "text/csv")

            token = secrets.token_urlsafe(32)
            await uow.exports.add(Export(
                id=export_id, user_id=ctx.user_id, file_key=file_key,
                download_token_hash=self._hasher.token_hash(token), created_at=now,
                expires_at=now + timedelta(seconds=self._s.export_ttl_seconds),
            ))
            await record_audit(uow, self._clock, AuditAction.EXPORT_CREATED,
                               user_id=ctx.user_id, device_id=ctx.device_id, rows=len(txs))
            await uow.commit()
        return ExportCreated(download_token=token,
                             expires_at=now + timedelta(seconds=self._s.export_ttl_seconds))

    async def download(self, token: str) -> bytes:
        """Havola egasi autentifikatsiyasiz yuklay oladi — faqat bir marta va 24 soat ichida."""
        now = self._clock.now()
        async with self._uow as uow:
            export = await uow.exports.get_by_token_hash(self._hasher.token_hash(token))
            if export is None or not export.is_downloadable(now):
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
        return data

    async def purge_expired(self) -> int:
        """Cron/worker chaqiradi: muddati o'tgan eksportlarni o'chiradi."""
        async with self._uow as uow:
            expired = await uow.exports.list_expired(self._clock.now())
            for e in expired:
                await self._storage.delete(e.file_key)
                await uow.exports.delete(e.id)
            await uow.commit()
        return len(expired)
