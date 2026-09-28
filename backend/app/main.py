from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

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

    # Tartib: tashqi → ichki. RequestId eng tashqarida, xatolarda ham request_id bo'lsin
    app.add_middleware(SecurityMiddleware, settings=settings)
    app.add_middleware(RequestIdMiddleware)
    return app
