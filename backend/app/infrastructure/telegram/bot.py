"""Telegram Bot API klienti (o'z botimiz orqali OTP).

- Token URL yo'lida bo'ladi — shuning uchun URL va javob tanasi hech qachon loglanmaydi.
- 403 (bot bloklangan) / 400 "chat not found" -> TelegramChatUnavailable (bog'lanish o'chadi).
- Boshqa xatolar -> ServiceUnavailableError; OTP bu holda SMS'ga o'tadi.
"""

import logging

import httpx

from app.application.common.interfaces import TelegramChatUnavailable
from app.domain.common.errors import ServiceUnavailableError

logger = logging.getLogger("finora.telegram")

API_BASE = "https://api.telegram.org"


class TelegramBotClient:
    def __init__(self, token: str, client: httpx.AsyncClient | None = None,
                 timeout: float = 5.0) -> None:
        self._client = client or httpx.AsyncClient(base_url=f"{API_BASE}/bot{token}",
                                                   timeout=timeout)

    async def _call(self, method: str, payload: dict[str, object],
                    http_timeout: float | None = None) -> dict[str, object]:
        try:
            if http_timeout is None:
                r = await self._client.post(f"/{method}", json=payload)
            else:
                r = await self._client.post(f"/{method}", json=payload, timeout=http_timeout)
        except httpx.HTTPError as exc:
            logger.error("telegram_transport_error", extra={"error": type(exc).__name__})
            raise ServiceUnavailableError() from None
        if r.status_code == 403 or (r.status_code == 400 and "chat not found" in r.text):
            raise TelegramChatUnavailable()
        if r.status_code >= 300:
            logger.error("telegram_send_failed", extra={"status": r.status_code})
            raise ServiceUnavailableError()
        data: dict[str, object] = r.json()
        return data

    async def send_message(self, chat_id: int, text: str,
                           reply_markup: dict[str, object] | None = None) -> None:
        payload: dict[str, object] = {"chat_id": chat_id, "text": text,
                                      "disable_web_page_preview": True}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        await self._call("sendMessage", payload)

    async def get_updates(self, offset: int | None,
                          poll_seconds: int) -> list[dict[str, object]]:
        """Long polling. Webhook o'rnatilgan bo'lsa Telegram 409 qaytaradi — avval
        delete_webhook chaqiriladi."""
        payload: dict[str, object] = {"timeout": poll_seconds,
                                      "allowed_updates": ["message", "my_chat_member"]}
        if offset is not None:
            payload["offset"] = offset
        data = await self._call("getUpdates", payload, http_timeout=poll_seconds + 10)
        result = data.get("result")
        return [u for u in result if isinstance(u, dict)] if isinstance(result, list) else []

    async def delete_webhook(self) -> None:
        await self._call("deleteWebhook", {"drop_pending_updates": False})

    async def set_webhook(self, url: str, secret: str) -> None:
        await self._call("setWebhook", {
            "url": url, "secret_token": secret, "drop_pending_updates": True,
            "allowed_updates": ["message", "my_chat_member"],
        })

    async def aclose(self) -> None:
        await self._client.aclose()
