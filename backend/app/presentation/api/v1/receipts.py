from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response, status

from app.application.receipts.use_cases import receipt_to_dict
from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.receipts import QrIn, ReceiptOut, ReceiptPageOut, SignedUrlOut

router = APIRouter(prefix="/receipts", tags=["receipts"], responses=ERROR_RESPONSES)


@router.post("/scan", status_code=status.HTTP_201_CREATED, response_model=ReceiptOut)
async def scan_receipt(request: Request, ctx: AuthDep, c: ContainerDep,
                       idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    """Tana — xom rasm baytlari (≤ 10 MB). Format Content-Type'dan emas, magic bytes'dan.
    O'qib bo'lmasa — 422 receipt_unreadable (BE-701)."""
    return await factories.receipts(c).upload(ctx, await request.body(), idempotency_key)


@router.post("/qr", status_code=status.HTTP_201_CREATED, response_model=ReceiptOut)
async def scan_qr(body: QrIn, ctx: AuthDep, c: ContainerDep,
                  idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    """Fiskal chek QR'i (ofd.soliq.uz). Fiskal emas — 422 qr_not_supported (BE-702)."""
    return await factories.receipts(c).from_qr(ctx, body.payload, idempotency_key)


@router.get("", response_model=ReceiptPageOut)
async def list_receipts(ctx: AuthDep, c: ContainerDep,
                        cursor: Annotated[str | None, Query(max_length=200)] = None,
                        limit: Annotated[int, Query(ge=1, le=100)] = 30) -> dict[str, Any]:
    page = await factories.receipts(c).list(ctx, cursor, limit)
    return {"items": [receipt_to_dict(r) for r in page.items], "next_cursor": page.next_cursor}


@router.get("/{receipt_id}", response_model=ReceiptOut)
async def get_receipt(receipt_id: UUID, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return receipt_to_dict(await factories.receipts(c).get(ctx, receipt_id))


@router.post("/{receipt_id}/url", response_model=SignedUrlOut)
async def receipt_url(receipt_id: UUID, ctx: AuthDep, c: ContainerDep,
                      request: Request) -> SignedUrlOut:
    """Rasm uchun 5 daqiqalik imzolangan URL (BE-703)."""
    signed = await factories.receipts(c).sign_url(ctx, receipt_id)
    expires_at = datetime.fromtimestamp(signed.expires_at, UTC)
    if signed.direct_url is not None:
        return SignedUrlOut(url=signed.direct_url, expires_at=expires_at)
    url = request.url_for("receipt_image", receipt_id=str(signed.receipt_id)).include_query_params(
        exp=signed.expires_at, sig=signed.signature
    )
    return SignedUrlOut(url=str(url), expires_at=expires_at)


@router.get("/{receipt_id}/image", name="receipt_image", include_in_schema=False)
async def receipt_image(
    receipt_id: UUID,
    c: ContainerDep,
    exp: Annotated[int, Query(ge=0, le=2**40)],
    sig: Annotated[str, Query(min_length=20, max_length=64)],
) -> Response:
    data, content_type = await factories.receipts(c).open_signed(receipt_id, exp, sig)
    return Response(content=data, media_type=content_type,
                    headers={"Content-Disposition": "inline"})


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(receipt_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await factories.receipts(c).delete(ctx, receipt_id)
