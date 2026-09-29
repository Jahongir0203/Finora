"""So'rov tili (BE-1601): `Accept-Language` -> locale_ctx.

Header bo'lmasa autentifikatsiyadan keyin user.language olinadi (deps.auth_context).
"""

from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.i18n import (
    DEFAULT_LANGUAGE,
    locale_ctx,
    locale_explicit_ctx,
    parse_accept_language,
)


class LocaleMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        header = dict(scope["headers"]).get(b"accept-language", b"")[:200].decode("latin-1")
        parsed = parse_accept_language(header)
        token = locale_ctx.set(parsed or DEFAULT_LANGUAGE)
        explicit = locale_explicit_ctx.set(parsed is not None)
        try:
            await self.app(scope, receive, send)
        finally:
            locale_ctx.reset(token)
            locale_explicit_ctx.reset(explicit)
