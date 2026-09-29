from datetime import date
from typing import Any

from fastapi import APIRouter

from app.application.stats.use_cases import StatsPeriod, StatsService
from app.presentation.api.deps import AuthDep, ContainerDep, TzDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.stats import StatsOut

router = APIRouter(tags=["stats"], responses=ERROR_RESPONSES)


@router.get("/stats", response_model=StatsOut)
async def stats(ctx: AuthDep, c: ContainerDep, tz: TzDep, period: StatsPeriod = StatsPeriod.MONTH,
                date: date | None = None) -> dict[str, Any]:
    """Faqat chiqimlar. Week — M..S, Month — W1..W5, Year — 12 oy. Foizlar yig'indisi 100.
    `has_enough_data=false` — birinchi tranzaksiyadan 7 kun o'tmagan (BE-801)."""
    now = c.clock.now()
    anchor = date or now.astimezone(tz).date()
    return await StatsService(c.uow()).execute(ctx.user_id, period, anchor, tz, now)
