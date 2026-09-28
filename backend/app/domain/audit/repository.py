from typing import Protocol

from app.domain.audit.entities import AuditEvent


class AuditRepository(Protocol):
    async def add(self, event: AuditEvent) -> None: ...
