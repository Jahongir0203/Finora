from fastapi import APIRouter

from app.application.insights.use_cases import AskInsights
from app.presentation.api.deps import AuthDep, ContainerDep
from app.presentation.schemas.insights import AskIn, AskOut

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ask", response_model=AskOut)
async def ask(body: AskIn, ctx: AuthDep, c: ContainerDep) -> AskOut:
    result = await AskInsights(c.uow(), c.insights, c.limiter, c.clock, c.settings).execute(
        ctx, body.question
    )
    return AskOut(answer=result.answer, window_days=result.window_days)
