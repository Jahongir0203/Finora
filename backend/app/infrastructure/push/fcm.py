"""Firebase Cloud Messaging, HTTP v1 API.

OAuth2 access token service account kaliti bilan imzolangan JWT (RS256) orqali olinadi
va ~55 daqiqa keshlanadi. Service account JSON Vault'dan keladi.
"""

import asyncio
import json
import time
from typing import Any

import httpx
import jwt

from app.application.common.interfaces import PushSendResult
from app.domain.notifications.entities import PushProvider

_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"
_TOKEN_URL = "https://oauth2.googleapis.com/token"  # noqa: S105 — URL, secret emas


class FcmSender:
    def __init__(self, service_account_json: str, client: httpx.AsyncClient | None = None) -> None:
        info: dict[str, Any] = json.loads(service_account_json)
        self._project = info["project_id"]
        self._email = info["client_email"]
        self._key = info["private_key"]
        self._token_uri = info.get("token_uri", _TOKEN_URL)
        self._client = client or httpx.AsyncClient(timeout=10.0)
        self._access: tuple[str, float] | None = None
        self._lock = asyncio.Lock()

    async def _access_token(self) -> str:
        async with self._lock:
            if self._access and self._access[1] > time.time() + 60:
                return self._access[0]
            now = int(time.time())
            assertion = jwt.encode(
                {"iss": self._email, "scope": _SCOPE, "aud": self._token_uri,
                 "iat": now, "exp": now + 3600},
                self._key, algorithm="RS256",
            )
            r = await self._client.post(self._token_uri, data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": assertion,
            })
            r.raise_for_status()
            data = r.json()
            self._access = (data["access_token"], now + int(data.get("expires_in", 3600)))
            return self._access[0]

    async def send(self, provider: PushProvider, token: str, title: str,
                   body: str) -> PushSendResult:
        try:
            access = await self._access_token()
            r = await self._client.post(
                f"https://fcm.googleapis.com/v1/projects/{self._project}/messages:send",
                headers={"Authorization": f"Bearer {access}"},
                json={"message": {"token": token,
                                  "notification": {"title": title, "body": body}}},
            )
        except (httpx.HTTPError, KeyError, ValueError):
            return PushSendResult.FAILED
        if r.status_code == 200:
            return PushSendResult.OK
        if r.status_code == 404 or "UNREGISTERED" in r.text or "INVALID_ARGUMENT" in r.text:
            return PushSendResult.INVALID_TOKEN
        return PushSendResult.FAILED

    async def aclose(self) -> None:
        await self._client.aclose()
