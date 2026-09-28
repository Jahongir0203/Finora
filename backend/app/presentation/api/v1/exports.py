from typing import Annotated

from fastapi import APIRouter, Path, Request, Response, status

from app.application.exports.use_cases import ExportService
from app.presentation.api.deps import AuthDep, ContainerDep
from app.presentation.schemas.transactions import ExportIn, ExportOut

router = APIRouter(prefix="/exports", tags=["exports"])


def _svc(c: ContainerDep) -> ExportService:
    return ExportService(c.uow(), c.storage, c.hasher, c.limiter, c.clock, c.settings)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ExportOut)
async def create_export(body: ExportIn, ctx: AuthDep, c: ContainerDep,
                        request: Request) -> ExportOut:
    created = await _svc(c).create(ctx, body.since, body.until)
    url = str(request.url_for("download_export", token=created.download_token))
    return ExportOut(download_url=url, expires_at=created.expires_at)


@router.get("/download/{token}", name="download_export")
async def download_export(
    token: Annotated[str, Path(min_length=20, max_length=128)], c: ContainerDep
) -> Response:
    data = await _svc(c).download(token)
    return Response(
        content=data,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="finora-export.csv"'},
    )
