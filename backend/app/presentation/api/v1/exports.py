from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Query, Request, Response, status

from app.application.exports.use_cases import export_to_dict
from app.domain.common.errors import ValidationFailedError
from app.domain.exports.entities import ExportFormat, ExportPeriod
from app.domain.transactions.entities import TransactionType
from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, TzDep, TzNameDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.exports import ExportCreateIn, ExportOut, ExportPreviewOut

router = APIRouter(prefix="/exports", tags=["exports"], responses=ERROR_RESPONSES)


def _parse_include(raw: str) -> list[TransactionType]:
    try:
        return [TransactionType(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError:
        raise ValidationFailedError(fields=["include"]) from None


@router.get("/preview", response_model=ExportPreviewOut)
async def preview(ctx: AuthDep, c: ContainerDep, tz: TzDep, period: ExportPeriod,
                  include: Annotated[str, Query(max_length=40)] = "expense,income,transfer",
                  format: ExportFormat = ExportFormat.PDF) -> dict[str, Any]:
    """Daily — bugun, Weekly — ISO hafta, Monthly — joriy oy, Yearly — yil boshidan (BE-601)."""
    return await factories.exports(c).preview(ctx, period, _parse_include(include), format, tz)


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=ExportOut)
async def create_export(body: ExportCreateIn, ctx: AuthDep, c: ContainerDep,
                        tz_name: TzNameDep, background: BackgroundTasks) -> dict[str, Any]:
    """Asinxron: `status: pending` qaytadi, holat `GET /v1/exports/{id}` bilan (BE-602).
    Limit: 10/soat. Bo'sh `include` — 422."""
    svc = factories.exports(c)
    export = await svc.create(ctx, body.period, body.include, body.format, tz_name)
    background.add_task(svc.process, export.id)
    return export_to_dict(export, None)


@router.get("/{export_id}", response_model=ExportOut)
async def export_status(export_id: UUID, ctx: AuthDep, c: ContainerDep,
                        request: Request) -> dict[str, Any]:
    """`ready` bo'lsa — 5 daqiqalik imzolangan, bir martalik `download_url`."""
    export, sig, exp = await factories.exports(c).status(ctx, export_id)
    url = None
    if sig is not None:
        url = str(request.url_for("download_export", export_id=str(export.id))
                  .include_query_params(exp=exp, sig=sig))
    return export_to_dict(export, url)


@router.get("/{export_id}/file", name="download_export", include_in_schema=False)
async def download_export(
    export_id: UUID, c: ContainerDep,
    exp: Annotated[int, Query(ge=0, le=2**40)],
    sig: Annotated[str, Query(min_length=20, max_length=64)],
) -> Response:
    data, content_type, name = await factories.exports(c).download(export_id, exp, sig)
    return Response(content=data, media_type=content_type,
                    headers={"Content-Disposition": f'attachment; filename="{name}"'})
