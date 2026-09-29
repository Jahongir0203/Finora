from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, LocaleDep, TzDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.insights import InsightActionIn, InsightActionOut, InsightListOut

router = APIRouter(prefix="/insights", tags=["insights"], responses=ERROR_RESPONSES)


@router.get("", response_model=InsightListOut)
async def list_insights(ctx: AuthDep, c: ContainerDep, tz: TzDep, locale: LocaleDep,
                        include_dismissed: bool = False) -> dict[str, Any]:
    """Qoidaga asoslangan tavsiyalar; matn user tilida (BE-901, BE-902 "Show dismissed")."""
    return await factories.insights(c).list(ctx, tz, locale, include_dismissed)


@router.post("/{insight_id}/dismiss", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss(insight_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await factories.insights(c).dismiss(ctx, insight_id)


@router.post("/{insight_id}/action", response_model=InsightActionOut)
async def act(insight_id: UUID, ctx: AuthDep, c: ContainerDep, tz: TzDep,
              body: InsightActionIn | None = None) -> dict[str, Any]:
    """set_budget → kategoriya limiti; remind_me → eslatma; turn_on_autosave → goal
    auto-save; review → reviewed (BE-902)."""
    params = body.model_dump(exclude_none=True) if body else {}
    return await factories.insights(c).act(ctx, insight_id, tz, params)
