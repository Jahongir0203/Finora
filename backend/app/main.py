import hmac
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import FastAPI, Header, Response
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text

from app.container import Container, build_container
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.metrics import REGISTRY
from app.domain.common.errors import AuthenticationError
from app.presentation.api.router import api_router
from app.presentation.errors import register_error_handlers
from app.presentation.middleware.locale import LocaleMiddleware
from app.presentation.middleware.request_id import RequestIdMiddleware
from app.presentation.middleware.security import SecurityMiddleware

logger = logging.getLogger("finora.app")


def create_app(settings: Settings | None = None, container: Container | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    container = container or build_container(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await container.aclose()

    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    app.state.container = container
    register_error_handlers(app)
    app.include_router(api_router)

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready", include_in_schema=False)
    async def ready() -> Response:
        """Readiness (BE-001): DB va Redis javob beryaptimi. Tafsilot tashqariga chiqmaydi."""
        checks = {"db": False, "cache": False}
        try:
            async with container.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["db"] = True
        except Exception:
            logger.exception("ready_db_failed")
        try:
            await container.kv.set("ready:ping", "1", 5)
            checks["cache"] = await container.kv.get("ready:ping") == "1"
        except Exception:
            logger.exception("ready_cache_failed")
        ok = all(checks.values())
        return Response(json.dumps({"status": "ok" if ok else "unavailable", **checks}),
                        status_code=200 if ok else 503, media_type="application/json")

    if settings.metrics_token is not None:
        metrics_token = settings.metrics_token.get_secret_value().encode()

        @app.get("/metrics", include_in_schema=False)
        async def metrics(authorization: Annotated[str | None, Header()] = None) -> Response:
            given = (authorization or "").removeprefix("Bearer ").encode()
            if not hmac.compare_digest(given, metrics_token):
                raise AuthenticationError()
            return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

    if settings.security_contact:
        contact = settings.security_contact

        # RFC 9116: mas'uliyatli oshkor qilish uchun aloqa (01-umumiy.md, 4-bo'lim, SHOULD)
        @app.get("/.well-known/security.txt", include_in_schema=False)
        async def security_txt() -> PlainTextResponse:
            expires = (datetime.now(UTC) + timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ")
            return PlainTextResponse(
                f"Contact: {contact}\nExpires: {expires}\nPreferred-Languages: uz, ru, en\n"
            )

    # Tartib: tashqi → ichki. RequestId eng tashqarida, xatolarda ham request_id bo'lsin
    app.add_middleware(LocaleMiddleware)
    app.add_middleware(SecurityMiddleware, settings=settings)
    app.add_middleware(RequestIdMiddleware)
    return app
