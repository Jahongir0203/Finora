"""Asosiy SMS provayderi ishlamasa zaxirasi orqali yuborish (BE-101)."""

import logging

from app.application.common.interfaces import SmsSender
from app.domain.common.errors import ServiceUnavailableError
from app.domain.common.values import PhoneNumber

logger = logging.getLogger("finora.sms")


class FallbackSmsSender:
    def __init__(self, primary: SmsSender, secondary: SmsSender) -> None:
        self._primary = primary
        self._secondary = secondary

    async def send(self, phone: PhoneNumber, text: str) -> None:
        try:
            await self._primary.send(phone, text)
        except ServiceUnavailableError:
            logger.warning("sms_fallback_used")
            await self._secondary.send(phone, text)

    async def aclose(self) -> None:
        for sender in (self._primary, self._secondary):
            close = getattr(sender, "aclose", None)
            if close is not None:
                await close()
