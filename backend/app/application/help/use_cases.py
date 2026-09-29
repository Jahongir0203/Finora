"""Yordam (BE-1701) va live chat sessiyasi (BE-1702)."""

import hashlib
import hmac
from typing import Any
from uuid import UUID

from app.application.common.uow import UnitOfWork
from app.core.config import Settings
from app.domain.common.errors import ServiceUnavailableError


class HelpService:
    def __init__(self, uow: UnitOfWork, settings: Settings) -> None:
        self._uow = uow
        self._s = settings

    async def faq(self, language: str) -> list[dict[str, Any]]:
        async with self._uow as uow:
            items = await uow.faq.for_language(language)
            if not items and language != "en":
                items = await uow.faq.for_language("en")
        return [{"id": str(i.id), "question": i.question, "answer": i.answer} for i in items]

    def contacts(self) -> dict[str, Any]:
        s = self._s
        return {"telegram": s.support_telegram, "phone": s.support_phone,
                "email": s.support_email, "live_chat": bool(s.support_chat_secret)}

    def chat_session(self, user_id: UUID) -> dict[str, Any]:
        """Tayyor chat servisi (Crisp / Intercom / Chatwoot) uchun identity verification:
        user_hash = HMAC-SHA256(secret, user_id). Telefon va ism yuborilmaydi."""
        if self._s.support_chat_secret is None:
            raise ServiceUnavailableError()
        secret = self._s.support_chat_secret.get_secret_value().encode()
        user_hash = hmac.new(secret, str(user_id).encode(), hashlib.sha256).hexdigest()
        return {"provider": self._s.support_chat_provider, "user_id": str(user_id),
                "user_hash": user_hash}
