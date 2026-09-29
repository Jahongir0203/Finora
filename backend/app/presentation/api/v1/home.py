from typing import Any

from fastapi import APIRouter

from app.application.home.use_cases import HomeService
from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep, LocaleDep, TimezoneHeader, TzDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.home import HomeOut

router = APIRouter(tags=["home"], responses=ERROR_RESPONSES)


@router.get("/home", response_model=HomeOut)
async def home(ctx: AuthDep, c: ContainerDep, tz: TzDep, locale: LocaleDep,
               x_timezone: TimezoneHeader = None) -> dict[str, Any]:
    """Butun Home ekrani bitta so'rovda (BE-301). Oy chegarasi `X-Timezone` bo'yicha."""
    return await HomeService(c.uow(), c.ledger, factories.insights(c)).execute(
        ctx.user_id, c.clock.now(), tz, x_timezone, locale)
