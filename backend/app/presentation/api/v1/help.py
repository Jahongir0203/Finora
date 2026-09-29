from typing import Annotated, Any

from fastapi import APIRouter, Query

from app.application.help.use_cases import HelpService
from app.core.i18n import normalize_language
from app.presentation.api.deps import AuthDep, ContainerDep, LocaleDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.misc import ContactsOut, FaqOut, SupportSessionOut

router = APIRouter(tags=["help"], responses=ERROR_RESPONSES)


@router.get("/help/faq", response_model=list[FaqOut])
async def faq(ctx: AuthDep, c: ContainerDep, locale: LocaleDep,
              lang: Annotated[str | None, Query(max_length=16)] = None) -> list[dict[str, Any]]:
    return await HelpService(c.uow(), c.settings).faq(normalize_language(lang) or locale)


@router.get("/help/contacts", response_model=ContactsOut)
async def contacts(ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    return HelpService(c.uow(), c.settings).contacts()


@router.post("/support/session", response_model=SupportSessionOut)
async def support_session(ctx: AuthDep, c: ContainerDep) -> dict[str, Any]:
    """Live chat (BE-1702): chat servisi uchun imzolangan identifikator. Sozlanmagan — 503."""
    return HelpService(c.uow(), c.settings).chat_session(ctx.user_id)
