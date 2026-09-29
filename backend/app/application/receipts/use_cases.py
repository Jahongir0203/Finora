"""Cheklar (BE-701..703; 02-backend.md, 4 va 6-bo'limlar).

Yuklash tartibi: magic bytes → antivirus → qayta kodlash (EXIF/GPS yo'q) → OCR → yopiq ombor.
Rasm faqat 5 daqiqalik imzolangan URL orqali ochiladi. Tranzaksiyaga bog'lanmagan
(tasdiqlanmagan) cheklar 24 soatdan keyin o'chiriladi.
"""

import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, timedelta
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import (
    Clock,
    FileStorage,
    FiscalReceiptProvider,
    ImageSanitizer,
    MalwareScanner,
    ReceiptOcr,
    UrlSigner,
)
from app.application.common.pagination import Page, clamp_limit, decode_cursor, encode_cursor
from app.application.common.rate_limit import HOUR, Limit, RateLimiter
from app.application.common.uow import UnitOfWork
from app.application.receipts.parsing import parse_fiscal_qr, suggest_category
from app.core.config import Settings
from app.domain.common.errors import (
    FileRejectedError,
    NotFoundError,
    OcrUnavailableError,
    QrNotSupportedError,
    ReceiptUnreadableError,
    UnsupportedMediaError,
)
from app.domain.common.ids import uuid7
from app.domain.receipts.entities import ParsedReceipt, Receipt, ReceiptSource

logger = logging.getLogger("finora.receipts")

UNCONFIRMED_TTL = timedelta(hours=24)


def receipt_resource(receipt_id: UUID) -> str:
    return f"receipt:{receipt_id}"


def receipt_to_dict(r: Receipt) -> dict[str, Any]:
    return {
        "receipt_id": str(r.id),
        "id": str(r.id),
        "source": r.source.value,
        "merchant": r.merchant,
        "total": r.total,
        "occurred_at": r.occurred_at.astimezone(UTC).isoformat() if r.occurred_at else None,
        "items": [i.to_dict() for i in r.items],
        "suggested_category_id": r.suggested_category_id,
        "confidence": round(r.confidence, 2),
        "has_image": r.file_key is not None,
        "confirmed": r.confirmed_at is not None,
        "created_at": r.created_at.isoformat(),
    }


@dataclass(frozen=True, slots=True)
class SignedReceiptUrl:
    receipt_id: UUID
    expires_at: int
    # Ombor (S3) presigned URL bergan bo'lsa — shu; aks holda API endpoint uchun HMAC imzo
    direct_url: str | None = None
    signature: str | None = None


def _usable(parsed: ParsedReceipt | None) -> bool:
    return parsed is not None and (parsed.total or 0) > 0


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
        ocr: ReceiptOcr | None = None,
        fiscal: FiscalReceiptProvider | None = None,
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
        self._ocr = ocr
        self._fiscal = fiscal

    async def _limit(self, ctx: AuthContext) -> None:
        await self._limiter.hit("receipts", str(ctx.user_id),
                                [Limit("hour", self._s.receipts_per_hour, HOUR)])

    async def upload(self, ctx: AuthContext, data: bytes,
                     idempotency_key: str | None) -> dict[str, Any]:
        await self._limit(ctx)
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
                if self._ocr is None:
                    raise OcrUnavailableError()
                parsed = await self._ocr.read(clean.data)
                if not _usable(parsed):
                    raise ReceiptUnreadableError()
                assert parsed is not None
                receipt_id = uuid7()
                file_key = f"receipts/{ctx.user_id}/{receipt_id}.jpg"
                await self._storage.put(file_key, clean.data, clean.content_type)
                receipt = Receipt(
                    id=receipt_id, user_id=ctx.user_id, created_at=self._clock.now(),
                    source=ReceiptSource.IMAGE, file_key=file_key,
                    content_type=clean.content_type, size_bytes=len(clean.data),
                    merchant=parsed.merchant, total=parsed.total,
                    occurred_at=parsed.occurred_at, items=parsed.items,
                    suggested_category_id=suggest_category(parsed.merchant, parsed.items),
                    confidence=parsed.confidence,
                )
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

    async def from_qr(self, ctx: AuthContext, payload: str,
                      idempotency_key: str | None) -> dict[str, Any]:
        """BE-702: fiskal chek QR'i -> ofd.soliq.uz ma'lumoti. Javob BE-701 bilan bir xil."""
        await self._limit(ctx)
        qr = parse_fiscal_qr(payload)
        if qr is None:
            raise QrNotSupportedError()
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                if self._fiscal is None:
                    raise OcrUnavailableError()
                parsed = await self._fiscal.fetch(qr.terminal_id, qr.receipt_number,
                                                  qr.fiscal_sign, qr.issued_at)
                if not _usable(parsed):
                    raise ReceiptUnreadableError()
                assert parsed is not None
                receipt = Receipt(
                    id=uuid7(), user_id=ctx.user_id, created_at=self._clock.now(),
                    source=ReceiptSource.QR, merchant=parsed.merchant, total=parsed.total,
                    occurred_at=parsed.occurred_at or qr.issued_at, items=parsed.items,
                    suggested_category_id=suggest_category(parsed.merchant, parsed.items),
                    confidence=max(parsed.confidence, 0.99), fiscal_sign=qr.fiscal_sign,
                )
                await uow.receipts.add(receipt)
                return receipt_to_dict(receipt)

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="receipt.qr",
                payload={"fiscal_sign": qr.fiscal_sign, "terminal": qr.terminal_id},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )

    async def list(self, ctx: AuthContext, cursor: str | None,
                   limit: int | None) -> Page[Receipt]:
        size = clamp_limit(limit)
        after = decode_cursor(cursor)
        async with self._uow as uow:
            rows = await uow.receipts.list_for_user(
                ctx.user_id, limit=size + 1, after=(after.at, after.id) if after else None)
        items = rows[:size]
        nxt = encode_cursor(items[-1].created_at, items[-1].id) if len(rows) > size else None
        return Page(items, nxt)

    async def get(self, ctx: AuthContext, receipt_id: UUID) -> Receipt:
        async with self._uow as uow:
            receipt = await uow.receipts.get_for_user(ctx.user_id, receipt_id)
        if receipt is None:
            raise NotFoundError()
        return receipt

    async def sign_url(self, ctx: AuthContext, receipt_id: UUID) -> SignedReceiptUrl:
        receipt = await self.get(ctx, receipt_id)
        if receipt.file_key is None:
            raise NotFoundError()
        ttl = self._s.receipt_url_ttl_seconds
        expires_at = int(self._clock.now().timestamp()) + ttl
        direct = await self._storage.presigned_get_url(receipt.file_key, ttl)
        if direct is not None:
            return SignedReceiptUrl(receipt_id=receipt.id, expires_at=expires_at,
                                    direct_url=direct)
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
        if receipt is None or receipt.file_key is None:
            raise NotFoundError()
        data = await self._storage.get(receipt.file_key)
        if data is None:
            raise NotFoundError()
        return data, receipt.content_type or "image/jpeg"

    async def delete(self, ctx: AuthContext, receipt_id: UUID) -> None:
        async with self._uow as uow:
            receipt = await uow.receipts.get_for_user(ctx.user_id, receipt_id)
            if receipt is None or not await uow.receipts.delete_for_user(ctx.user_id, receipt_id):
                raise NotFoundError()
            await uow.commit()
        if receipt.file_key:
            await self._storage.delete(receipt.file_key)

    async def purge_unconfirmed(self) -> int:
        """Job: 24 soatdan eski tasdiqlanmagan cheklar (BE-703)."""
        async with self._uow as uow:
            stale = await uow.receipts.unconfirmed_before(self._clock.now() - UNCONFIRMED_TTL)
            for r in stale:
                await uow.receipts.delete(r.id)
            await uow.commit()
        for r in stale:
            if r.file_key:
                await self._storage.delete(r.file_key)
        return len(stale)
