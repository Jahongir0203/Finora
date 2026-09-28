"""Cheklar (02-backend.md, 4 va 6-bo'limlar).

Yuklash tartibi: magic bytes → antivirus → qayta kodlash (EXIF/GPS yo'q) → yopiq ombor.
Rasm faqat 5 daqiqalik imzolangan URL orqali ochiladi.
"""

import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import (
    Clock,
    FileStorage,
    ImageSanitizer,
    MalwareScanner,
    UrlSigner,
)
from app.application.common.rate_limit import HOUR, Limit, RateLimiter
from app.application.common.uow import UnitOfWork
from app.core.config import Settings
from app.domain.common.errors import FileRejectedError, NotFoundError, UnsupportedMediaError
from app.domain.common.ids import uuid7
from app.domain.receipts.entities import Receipt

logger = logging.getLogger("finora.receipts")


def receipt_resource(receipt_id: UUID) -> str:
    return f"receipt:{receipt_id}"


def receipt_to_dict(r: Receipt) -> dict[str, Any]:
    return {
        "id": str(r.id),
        "content_type": r.content_type,
        "size_bytes": r.size_bytes,
        "created_at": r.created_at.isoformat(),
    }


@dataclass(frozen=True, slots=True)
class SignedReceiptUrl:
    receipt_id: UUID
    expires_at: int
    signature: str


class ReceiptService:
    def __init__(
        self,
        uow: UnitOfWork,
        storage: FileStorage,
        scanner: MalwareScanner,
        sanitizer: ImageSanitizer,
        signer: UrlSigner,
        limiter: RateLimiter,
        clock: Clock,
        settings: Settings,
        sniff: Callable[[bytes], str | None],
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._scanner = scanner
        self._sanitizer = sanitizer
        self._signer = signer
        self._limiter = limiter
        self._clock = clock
        self._s = settings
        self._sniff = sniff

    async def upload(self, ctx: AuthContext, data: bytes,
                     idempotency_key: str | None) -> dict[str, Any]:
        await self._limiter.hit("receipts", str(ctx.user_id),
                                [Limit("hour", self._s.receipts_per_hour, HOUR)])
        if not data or len(data) > self._s.max_receipt_bytes:
            raise FileRejectedError()
        fmt = self._sniff(data)
        if fmt is None:
            raise UnsupportedMediaError()

        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                if not await self._scanner.is_clean(data):
                    raise FileRejectedError()
                clean = self._sanitizer.sanitize(data, fmt)
                receipt_id = uuid7()
                file_key = f"receipts/{ctx.user_id}/{receipt_id}.jpg"
                await self._storage.put(file_key, clean.data, clean.content_type)
                receipt = Receipt(id=receipt_id, user_id=ctx.user_id, file_key=file_key,
                                  content_type=clean.content_type, size_bytes=len(clean.data),
                                  created_at=self._clock.now())
                try:
                    await uow.receipts.add(receipt)
                except Exception:
                    await self._storage.delete(file_key)
                    raise
                return receipt_to_dict(receipt)

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="receipt.upload",
                payload={"sha256": hashlib.sha256(data).hexdigest()},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )

    async def list(self, ctx: AuthContext) -> list[Receipt]:
        async with self._uow as uow:
            return await uow.receipts.list_for_user(ctx.user_id)

    async def get(self, ctx: AuthContext, receipt_id: UUID) -> Receipt:
        async with self._uow as uow:
            receipt = await uow.receipts.get_for_user(ctx.user_id, receipt_id)
        if receipt is None:
            raise NotFoundError()
        return receipt

    async def sign_url(self, ctx: AuthContext, receipt_id: UUID) -> SignedReceiptUrl:
        receipt = await self.get(ctx, receipt_id)
        expires_at = int(self._clock.now().timestamp()) + self._s.receipt_url_ttl_seconds
        return SignedReceiptUrl(
            receipt_id=receipt.id, expires_at=expires_at,
            signature=self._signer.sign(receipt_resource(receipt.id), expires_at),
        )

    async def open_signed(self, receipt_id: UUID, expires_at: int,
                          signature: str) -> tuple[bytes, str]:
        """Imzo — egalik isboti. Noto'g'ri/eskirgan imzo ham, yo'q chek ham 404."""
        now = int(self._clock.now().timestamp())
        if not self._signer.verify(receipt_resource(receipt_id), expires_at, signature, now):
            raise NotFoundError()
        async with self._uow as uow:
            receipt = await uow.receipts.get(receipt_id)
        if receipt is None:
            raise NotFoundError()
        data = await self._storage.get(receipt.file_key)
        if data is None:
            raise NotFoundError()
        return data, receipt.content_type

    async def delete(self, ctx: AuthContext, receipt_id: UUID) -> None:
        async with self._uow as uow:
            receipt = await uow.receipts.get_for_user(ctx.user_id, receipt_id)
            if receipt is None or not await uow.receipts.delete_for_user(ctx.user_id, receipt_id):
                raise NotFoundError()
            await uow.commit()
        await self._storage.delete(receipt.file_key)


def expires_at_to_datetime(ts: int, clock: Clock) -> datetime:
    return datetime.fromtimestamp(ts, tz=clock.now().tzinfo)
