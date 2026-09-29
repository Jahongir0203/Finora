from typing import Any

from fastapi import APIRouter
from pydantic import AwareDatetime

from app.application.sync.use_cases import SyncService
from app.presentation.api.deps import AuthDep, ContainerDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.misc import SyncOut

router = APIRouter(tags=["sync"], responses=ERROR_RESPONSES)


@router.get("/sync", response_model=SyncOut)
async def sync(since: AwareDatetime, ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    """`since` dan keyin o'zgargan/o'chirilgan yozuvlar (BE-302). Keyingi so'rov uchun
    javobdagi `server_time` ni `since` sifatida yuboring; `has_more` — yana chaqiring."""
    return await SyncService(c.uow(), c.ledger).execute(ctx.user_id, since, c.clock.now())


