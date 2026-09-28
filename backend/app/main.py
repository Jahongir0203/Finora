from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from app.container import Container, build_container
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.presentation.api.router import api_router
from app.presentation.errors import register_error_handlers
from app.presentation.middleware.request_id import RequestIdMiddleware
from app.presentation.middleware.security import SecurityMiddleware


def create_app(settings: Settings | None = None, container: Container | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    container = container or build_container(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await container.engine.dispose()

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
    app.add_middleware(SecurityMiddleware, settings=settings)
    app.add_middleware(RequestIdMiddleware)
    return app
