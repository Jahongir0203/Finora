import re
import secrets
import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import request_id_ctx
from app.core.metrics import http_latency, http_responses

_VALID = re.compile(r"^[A-Za-z0-9\-]{8,64}$")


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope["headers"]).get(b"x-request-id", b"").decode("latin-1")
        rid = incoming if _VALID.fullmatch(incoming) else secrets.token_hex(12)
        token = request_id_ctx.set(rid)

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                http_responses.labels(status=str(message["status"])).inc()
                message.setdefault("headers", []).append((b"x-request-id", rid.encode()))
            await send(message)

        started = time.perf_counter()
        try:
            await self.app(scope, receive, send_with_id)
        finally:
            route = getattr(scope.get("route"), "path_format", None) or "unmatched"
            http_latency.labels(method=scope.get("method", ""), route=route).observe(
                time.perf_counter() - started)
            request_id_ctx.reset(token)
