import logging
from uuid import UUID

logger = logging.getLogger("finora.notifications")


class LogNotifier:
    """Push provayderi (FCM/APNs) ulanguncha — faqat hodisani loglaydi."""

    async def new_sign_in(self, user_id: UUID, exclude_device_id: UUID, device_name: str) -> None:
        logger.info("notify_new_sign_in", extra={"user_id": str(user_id)})

    async def sessions_revoked(self, user_id: UUID, reason: str) -> None:
        logger.info("notify_sessions_revoked", extra={"user_id": str(user_id), "reason": reason})
