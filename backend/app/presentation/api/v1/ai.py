from fastapi import APIRouter

from app.application.insights.use_cases import AskInsights, suggestions
from app.presentation.api.deps import AuthDep, ContainerDep, LocaleDep, TzDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.insights import AskIn, AskOut, SuggestionsOut

router = APIRouter(prefix="/ai", tags=["ai"], responses=ERROR_RESPONSES)


@router.post("/ask", response_model=AskOut)
async def ask(body: AskIn, ctx: AuthDep, c: ContainerDep, tz: TzDep,
              locale: LocaleDep) -> AskOut:
    """Oddiy matn, user tilida, ≤ 600 belgi. Limit 20/soat, 100/kun. 15 s — 503 ai_unavailable."""
    result = await AskInsights(c.uow(), c.insights, c.limiter, c.clock, c.settings).execute(
        ctx, body.question, locale=locale, tz=tz
    )
    return AskOut(answer=result.answer, window_days=result.window_days)


@router.get("/suggestions", response_model=SuggestionsOut)
async def ai_suggestions(ctx: AuthDep, locale: LocaleDep) -> SuggestionsOut:
    """Tayyor savollar — so'rov tilida (Accept-Language, bo'lmasa user.language)."""
    return SuggestionsOut(items=suggestions(locale))
