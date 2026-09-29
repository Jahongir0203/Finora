"""PlayMobile (smsxabar.uz) SMS adapteri — Eskiz'ga zaxira provayder (BE-101).

Broker API: `POST /send` (Basic auth), JSON {messages: [{recipient, message-id, sms: {...}}]}.
SMS matni, javob tanasi va to'liq raqam loglanmaydi; xatolar 503 ga aylanadi.
"""

import logging
import secrets

import httpx

from app.core.config import Settings
from app.domain.common.errors import ServiceUnavailableError
from app.domain.common.values import PhoneNumber

logger = logging.getLogger("finora.sms")


class PlayMobileSmsSender:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        if not settings.playmobile_login or settings.playmobile_password is None:
            raise ValueError("FINORA_PLAYMOBILE_LOGIN va FINORA_PLAYMOBILE_PASSWORD majburiy")
        self._originator = settings.playmobile_originator
        self._client = client or httpx.AsyncClient(
            base_url=settings.playmobile_base_url, timeout=settings.sms_timeout_seconds,
            auth=(settings.playmobile_login, settings.playmobile_password.get_secret_value()),
        )

    async def send(self, phone: PhoneNumber, text: str) -> None:
        body = {"messages": [{
            "recipient": phone.value.lstrip("+"),
            "message-id": "fn" + secrets.token_hex(8),
            "sms": {"originator": self._originator, "content": {"text": text}},
        }]}
        try:
            r = await self._client.post("/send", json=body)
        except httpx.HTTPError as exc:
            logger.error("sms_transport_error", extra={"error": type(exc).__name__})
            raise ServiceUnavailableError() from None
        if r.status_code >= 300:
            logger.error("sms_send_failed", extra={"status": r.status_code})
            raise ServiceUnavailableError()

    async def aclose(self) -> None:
        await self._client.aclose()
