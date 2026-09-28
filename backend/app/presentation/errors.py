"""Yagona xato formati: { code, message, request_id }. Stack trace, SQL, ichki yo'llar yo'q."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import request_id_ctx
from app.domain.common.errors import (
    AuthenticationError,
    ConflictError,
    DomainError,
    FileRejectedError,
    IdempotencyConflictError,
    IdempotencyKeyRequiredError,
    InsufficientFundsError,
    InvalidOtpError,
    NotFoundError,
    RateLimitedError,
    ServiceUnavailableError,
    UnsupportedMediaError,
    ValidationFailedError,
)

logger = logging.getLogger("finora.errors")

_STATUS: list[tuple[type[DomainError], int]] = [
    (NotFoundError, 404),
    (RateLimitedError, 429),
    (AuthenticationError, 401),
    (InsufficientFundsError, 422),
    (ValidationFailedError, 422),
    (InvalidOtpError, 400),
    (IdempotencyKeyRequiredError, 400),
    (IdempotencyConflictError, 409),
    (UnsupportedMediaError, 415),
    (ConflictError, 409),
    (ServiceUnavailableError, 503),
    (FileRejectedError, 422),
]

_HTTP_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    413: "payload_too_large",
    415: "unsupported_media_type",
}


def error_response(status: int, code: str, message: str,
                   headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"code": code, "message": message, "request_id": request_id_ctx.get()},
        headers=headers,
    )


async def _domain_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    status = next((s for cls, s in _STATUS if isinstance(exc, cls)), 400)
    headers: dict[str, str] = {}
    if isinstance(exc, RateLimitedError):
        headers["Retry-After"] = str(exc.retry_after)
    if isinstance(exc, AuthenticationError):
        headers["WWW-Authenticate"] = "Bearer"
    return error_response(status, exc.code, exc.message, headers)


async def _validation_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    # Faqat maydon yo'li — kiritilgan qiymat qaytarilmaydi (u sezgir bo'lishi mumkin)
    fields = sorted({".".join(str(p) for p in e.get("loc", ())[1:]) for e in exc.errors()})
    return error_response(422, "validation_error", "Noto'g'ri maydon(lar): " + ", ".join(fields))


async def _http_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code = _HTTP_CODES.get(exc.status_code, "error")
    message = exc.detail if isinstance(exc.detail, str) and exc.status_code < 500 else "Xatolik"
    return error_response(exc.status_code, code, message, dict(exc.headers or {}))


async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_error")
    return error_response(500, "internal_error", "Ichki xatolik. Keyinroq urinib ko'ring")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(Exception, _unhandled)
