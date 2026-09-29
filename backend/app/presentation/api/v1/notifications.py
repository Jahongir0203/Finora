from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.application.notifications.use_cases import NotificationService
from app.presentation.api.deps import AuthDep, ContainerDep
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.notifications import (
    CountOut,
    NotificationOut,
    NotificationPageOut,
)

router = APIRouter(prefix="/notifications", tags=["notifications"], responses=ERROR_RESPONSES)


def _svc(c: ContainerDep) -> NotificationService:
    return NotificationService(c.uow(), c.clock)


@router.get("", response_model=NotificationPageOut)
async def list_notifications(
    ctx: AuthDep, c: ContainerDep, cursor: Annotated[str | None, Query(max_length=200)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
) -> NotificationPageOut:
    """Today / Earlier guruhlash mijozda (vaqt zonasi bo'yicha)."""
    page, unread = await _svc(c).list(ctx, cursor, limit)
    return NotificationPageOut(
        items=[NotificationOut(id=n.id, type=n.type, title=n.title, body=n.body,
                               created_at=n.created_at, read=n.read_at is not None,
                               deep_link=n.deep_link) for n in page.items],
        next_cursor=page.next_cursor, unread=unread)


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(notification_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    await _svc(c).mark_read(ctx, notification_id)


@router.post("/read-all", response_model=CountOut)
async def mark_all_read(ctx: AuthDep, c: ContainerDep) -> CountOut:
    return CountOut(count=await _svc(c).mark_all_read(ctx))


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(notification_id: UUID, ctx: AuthDep, c: ContainerDep) -> None:
    """Bittasini o'chirish (swipe) — soft delete, IDOR: faqat o'ziniki."""
    await _svc(c).delete(ctx, notification_id)


@router.delete("", response_model=CountOut)
async def clear(ctx: AuthDep, c: ContainerDep) -> CountOut:
    """"Clear" — soft delete."""
    return CountOut(count=await _svc(c).clear(ctx))
