from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response, status

from app.application.receipts.use_cases import ReceiptService, receipt_to_dict
from app.infrastructure.files.images import sniff_image_format
from app.presentation.api.deps import AuthDep, ContainerDep, IdempotencyKey
from app.presentation.schemas.receipts import ReceiptOut, SignedUrlOut

router = APIRouter(prefix="/receipts", tags=["receipts"])


def _svc(c: ContainerDep) -> ReceiptService:
    return ReceiptService(c.uow(), c.storage, c.scanner, c.sanitizer, c.signer, c.limiter,
                          c.clock, c.settings, sniff_image_format)


@router.post("/scan", status_code=status.HTTP_201_CREATED, response_model=ReceiptOut)
async def scan_receipt(request: Request, ctx: AuthDep, c: ContainerDep,
                       idempotency_key: IdempotencyKey = None) -> dict[str, Any]:
    """Tana — xom rasm baytlari (≤ 10 MB). Format Content-Type'dan emas, magic bytes'dan."""
    return await _svc(c).upload(ctx, await request.body(), idempotency_key)


@router.get("", response_model=list[ReceiptOut])
async def list_receipts(ctx: AuthDep, c: ContainerDep) -> list[dict[str, Any]]:
    return [receipt_to_dict(r) for r in await _svc(c).list(ctx)]


@router.get("/{receipt_id}", response_model=ReceiptOut)
async def get_receipt(receipt_id: UUID, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return receipt_to_dict(await _svc(c).get(ctx, receipt_id))


@router.post("/{receipt_id}/url", response_model=SignedUrlOut)
async def receipt_url(receipt_id: UUID, ctx: AuthDep, c: ContainerDep,
                      request: Request) -> SignedUrlOut:
    signed = await _svc(c).sign_url(ctx, receipt_id)
    url = request.url_for("receipt_image", receipt_id=str(signed.receipt_id)).include_query_params(
        exp=signed.expires_at, sig=signed.signature
    )
    return SignedUrlOut(url=str(url), expires_at=datetime.fromtimestamp(signed.expires_at, UTC))


@router.get("/{receipt_id}/image", name="receipt_image", include_in_schema=False)
async def receipt_image(
    receipt_id: UUID,
    c: ContainerDep,
    exp: Annotated[int, Query(ge=0, le=2**40)],
    sig: Annotated[str, Query(min_length=20, max_length=64)],
) -> Response:
    data, content_type = await _svc(c).open_signed(receipt_id, exp, sig)
    return Response(content=data, media_type=content_type,
                    headers={"Content-Disposition": "inline"})


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(receipt_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await _svc(c).delete(ctx, receipt_id)
