"""TLS majburiyligi, xavfsizlik sarlavhalari, so'rov hajmi cheklovi (02-backend.md, 4-bo'lim)."""

import json

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import Settings
from app.core.logging import request_id_ctx

SECURITY_HEADERS = [
    (b"strict-transport-security", b"max-age=31536000; includeSubDomains"),
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"no-referrer"),
    (b"cache-control", b"no-store"),
    (b"content-security-policy", b"default-src 'none'; frame-ancestors 'none'"),
]

# 10 MB faqat chek yuklash endpointi uchun, qolgan hamma joyda 1 MB
RECEIPT_UPLOAD_PATH = "/v1/receipts/scan"
_EXEMPT_PATHS = {"/health"}


async def _send_error(send: Send, status: int, code: str, message: str) -> None:
    body = json.dumps(
        {"code": code, "message": message, "request_id": request_id_ctx.get()}
    ).encode()
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()), *SECURITY_HEADERS],
    })
    await send({"type": "http.response.body", "body": body})


class _BodyTooLarge(Exception):
    pass


class SecurityMiddleware:
    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        self.app = app
        self.s = settings

    def _is_https(self, scope: Scope) -> bool:
        if self.s.trust_forwarded_proto:
            proto = dict(scope["headers"]).get(b"x-forwarded-proto")
            if proto is not None:
                return bool(proto.split(b",")[0].strip() == b"https")
        return bool(scope.get("scheme") == "https")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path: str = scope["path"]

        if self.s.enforce_https and path not in _EXEMPT_PATHS and not self._is_https(scope):
            await _send_error(send, 403, "https_required", "Faqat HTTPS orqali")
            return

        limit = (self.s.max_receipt_bytes if path == RECEIPT_UPLOAD_PATH
                 else self.s.max_body_bytes)
        declared = dict(scope["headers"]).get(b"content-length")
        if declared is not None:
            try:
                if int(declared) > limit:
                    await _send_error(send, 413, "payload_too_large", "So'rov hajmi juda katta")
                    return
            except ValueError:
                await _send_error(send, 400, "bad_request", "Noto'g'ri Content-Length")
                return

        received = 0
        response_started = False

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    raise _BodyTooLarge()
            return message

        async def send_with_headers(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
                headers = [h for h in message.get("headers", []) if h[0] != b"server"]
                existing = {h[0] for h in headers}
                headers += [h for h in SECURITY_HEADERS if h[0] not in existing]
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, limited_receive, send_with_headers)
        except _BodyTooLarge:
            if not response_started:
                await _send_error(send, 413, "payload_too_large", "So'rov hajmi juda katta")
