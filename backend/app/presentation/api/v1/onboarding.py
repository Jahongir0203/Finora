from typing import Any

from fastapi import APIRouter

from app.presentation.api import factories
from app.presentation.api.deps import AuthDep, ContainerDep
from app.presentation.schemas.accounts import OnboardingBalanceIn, OnboardingBalanceOut
from app.presentation.schemas.common import ERROR_RESPONSES

router = APIRouter(prefix="/onboarding", tags=["onboarding"], responses=ERROR_RESPONSES)


@router.post("/balance", response_model=OnboardingBalanceOut)
async def starting_balance(body: OnboardingBalanceIn, ctx: AuthDep,
                           c: ContainerDep) -> dict[str, Any]:
    """Boshlang'ich balans hisobning opening_balance'i (tranzaksiya emas). Qayta chaqirilsa
    yangilanadi, dublikat hisob yaratilmaydi (BE-204). "Skip" — so'rov yuborilmaydi."""
    return await factories.onboarding(c).execute(ctx, body.amount, body.location)
