from typing import Any

from fastapi import APIRouter

from app.application.currencies.use_cases import CurrencyService
from app.presentation.api.deps import AuthDep, ContainerDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.misc import CurrencyOut

router = APIRouter(tags=["currencies"], responses=ERROR_RESPONSES)


@router.get("/currencies", response_model=list[CurrencyOut])
async def currencies(ctx: AuthDep, c: ContainerDep) -> list[dict[str, Any]]:
    """Kurslar CBU'dan kuniga bir marta (BE-1602). Summalar bazada UZS'da qoladi."""
    return await CurrencyService(c.uow(), c.clock).list()
