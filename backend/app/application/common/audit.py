from typing import Any
from uuid import UUID

from app.application.common.interfaces import Clock
from app.application.common.uow import UnitOfWork
from app.domain.audit.entities import AuditAction, AuditEvent
from app.domain.common.ids import uuid7


async def record_audit(
    uow: UnitOfWork,
    clock: Clock,
    action: AuditAction,
    *,
    user_id: UUID | None,
    device_id: UUID | None = None,
    ip: str | None = None,
    **meta: Any,
) -> None:
    await uow.audit.add(
        AuditEvent(
            id=uuid7(),
            user_id=user_id,
            action=action,
            created_at=clock.now(),
            device_id=device_id,
            ip=ip,
            meta=meta,
        )
    )
