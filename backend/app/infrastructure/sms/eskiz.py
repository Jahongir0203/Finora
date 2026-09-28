"""Eskiz.uz SMS adapteri.

- Token `POST /auth/login` orqali olinadi va xotirada saqlanadi; 401 bo'lsa bir marta qayta login.
- SMS matnida OTP bor — matn, javob tanasi va to'liq raqam hech qachon loglanmaydi.
- Xatolar `ServiceUnavailableError` (503) ga aylanadi: mijoz provayder tafsilotini ko'rmaydi.
"""

import asyncio
import logging

import httpx

from app.core.config import Settings
from app.domain.common.errors import ServiceUnavailableError
from app.domain.common.values import PhoneNumber

logger = logging.getLogger("finora.sms")


class EskizSmsSender:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        if not settings.eskiz_email or settings.eskiz_password is None:
            raise ValueError("FINORA_ESKIZ_EMAIL va FINORA_ESKIZ_PASSWORD majburiy")
        self._email = settings.eskiz_email
        self._password = settings.eskiz_password
        self._sender = settings.eskiz_sender
        self._client = client or httpx.AsyncClient(
            base_url=settings.eskiz_base_url, timeout=settings.sms_timeout_seconds
        )
        self._token: str | None = None
        self._lock = asyncio.Lock()

    async def _login(self) -> str:
        r = await self._client.post("/auth/login", data={
            "email": self._email, "password": self._password.get_secret_value(),
        })
        if r.status_code != 200:
            logger.error("sms_auth_failed", extra={"status": r.status_code})
            raise ServiceUnavailableError()
        token = r.json().get("data", {}).get("token")
        if not isinstance(token, str) or not token:
            raise ServiceUnavailableError()
        return token

    async def _get_token(self, *, force: bool = False) -> str:
        async with self._lock:
            if force or self._token is None:
                self._token = await self._login()
            return self._token

    async def _post(self, token: str, phone: PhoneNumber, text: str) -> httpx.Response:
        return await self._client.post(
            "/message/sms/send",
            headers={"Authorization": f"Bearer {token}"},
            data={"mobile_phone": phone.value.lstrip("+"), "message": text,
                  "from": self._sender},
        )

    async def send(self, phone: PhoneNumber, text: str) -> None:
        try:
            r = await self._post(await self._get_token(), phone, text)
            if r.status_code == 401:
                r = await self._post(await self._get_token(force=True), phone, text)
        except httpx.HTTPError as exc:
            logger.error("sms_transport_error", extra={"error": type(exc).__name__})
            raise ServiceUnavailableError() from None
        if r.status_code >= 300:
            logger.error("sms_send_failed", extra={"status": r.status_code})
            raise ServiceUnavailableError()

    async def aclose(self) -> None:
        await self._client.aclose()
