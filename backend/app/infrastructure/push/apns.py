"""Apple Push Notification service: token-based auth (ES256 .p8 kalit), HTTP/2."""

import time

import httpx
import jwt

from app.application.common.interfaces import PushSendResult
from app.domain.notifications.entities import PushProvider

_PROD = "https://api.push.apple.com"
_SANDBOX = "https://api.sandbox.push.apple.com"
_TOKEN_TTL = 50 * 60  # Apple: 20-60 daqiqada yangilash


class ApnsSender:
    def __init__(self, team_id: str, key_id: str, private_key_pem: str, bundle_id: str,
                 *, sandbox: bool = False, client: httpx.AsyncClient | None = None) -> None:
        self._team = team_id
        self._key_id = key_id
        self._key = private_key_pem
        self._topic = bundle_id
        self._base = _SANDBOX if sandbox else _PROD
        self._client = client or httpx.AsyncClient(http2=True, timeout=10.0)
        self._jwt: tuple[str, float] | None = None

    def _provider_token(self) -> str:
        now = time.time()
        if self._jwt is None or self._jwt[1] < now:
            token = jwt.encode({"iss": self._team, "iat": int(now)}, self._key,
                               algorithm="ES256", headers={"kid": self._key_id})
            self._jwt = (token, now + _TOKEN_TTL)
        return self._jwt[0]

    async def send(self, provider: PushProvider, token: str, title: str,
                   body: str) -> PushSendResult:
        if not token.isalnum() or len(token) > 200:  # APNs token — hex
            return PushSendResult.INVALID_TOKEN
        try:
            r = await self._client.post(
                f"{self._base}/3/device/{token}",
                headers={"authorization": f"bearer {self._provider_token()}",
                         "apns-topic": self._topic, "apns-push-type": "alert",
                         "apns-priority": "10"},
                json={"aps": {"alert": {"title": title, "body": body}, "sound": "default"}},
            )
        except httpx.HTTPError:
            return PushSendResult.FAILED
        if r.status_code == 200:
            return PushSendResult.OK
        if r.status_code == 410 or "BadDeviceToken" in r.text or "Unregistered" in r.text:
            return PushSendResult.INVALID_TOKEN
        return PushSendResult.FAILED

    async def aclose(self) -> None:
        await self._client.aclose()
