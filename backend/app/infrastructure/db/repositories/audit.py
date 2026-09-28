from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.audit.entities import AuditEvent
from app.infrastructure.db.models import AuditLogModel


class SqlAuditRepository:
    """Faqat INSERT. Yangilash/o'chirish metodlari ataylab yo'q."""

    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def add(self, event: AuditEvent) -> None:
        self._s.add(AuditLogModel(
            id=event.id, user_id=event.user_id, action=event.action.value,
            device_id=event.device_id, ip=event.ip, meta=event.meta, created_at=event.created_at,
        ))
