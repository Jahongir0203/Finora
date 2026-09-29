"""FastAPI dependency'lari: container, autentifikatsiya, qurilma imzosi, use-case fabrikalari."""

from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, Header, Request

from app.application.auth.dto import AuthContext
from app.application.auth.sessions import Authenticate
from app.application.auth.tokens import TokenIssuer
from app.application.common.device_proof import DeviceProof
from app.application.common.rate_limit import MINUTE, Limit
from app.container import Container
from app.core.i18n import locale_ctx, locale_explicit_ctx
from app.domain.common.errors import AuthenticationError, InvalidDeviceSignatureError
from app.domain.common.time import DEFAULT_TZ_NAME, tz_or_default


def get_container(request: Request) -> Container:
    return request.app.state.container  # type: ignore[no-any-return]


ContainerDep = Annotated[Container, Depends(get_container)]


def client_ip(request: Request) -> str:
    # uvicorn --proxy-headers --forwarded-allow-ips=<gateway> bilan ishonchli IP
    return request.client.host if request.client else "unknown"


def token_issuer(c: ContainerDep) -> TokenIssuer:
    return TokenIssuer(c.access_tokens, c.hasher, c.clock, c.settings)


async def auth_context(
    c: ContainerDep,
    authorization: Annotated[str | None, Header()] = None,
) -> AuthContext:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError()
    ctx = await Authenticate(c.uow(), c.access_tokens).execute(authorization[7:].strip())
    if not locale_explicit_ctx.get():
        async with c.uow() as uow:
            user = await uow.users.get(ctx.user_id)
        if user is not None:
            locale_ctx.set(user.language)
    await c.limiter.hit(
        "user", str(ctx.user_id),
        [Limit("minute", c.settings.default_user_rate_per_minute, MINUTE)],
    )
    return ctx


AuthDep = Annotated[AuthContext, Depends(auth_context)]


async def device_proof(
    request: Request,
    x_device_timestamp: Annotated[str | None, Header()] = None,
    x_device_signature: Annotated[str | None, Header()] = None,
) -> DeviceProof:
    if not x_device_timestamp or not x_device_signature or len(x_device_signature) > 256:
        raise InvalidDeviceSignatureError()
    return DeviceProof(
        method=request.method,
        path=request.url.path,
        timestamp=x_device_timestamp,
        body=await request.body(),
        signature_b64=x_device_signature,
    )


DeviceProofDep = Annotated[DeviceProof, Depends(device_proof)]
TokenIssuerDep = Annotated[TokenIssuer, Depends(token_issuer)]
IdempotencyKey = Annotated[str | None, Header(alias="Idempotency-Key")]


def timezone_name(
    x_timezone: Annotated[str | None, Header(max_length=64)] = None,
) -> str:
    """Mijoz vaqt zonasi (`X-Timezone: Asia/Tashkent`). Noto'g'ri bo'lsa — standart."""
    tz = tz_or_default(x_timezone)
    return str(tz) if x_timezone and str(tz) == x_timezone else DEFAULT_TZ_NAME


def request_timezone(name: Annotated[str, Depends(timezone_name)]) -> ZoneInfo:
    return tz_or_default(name)


def request_locale() -> str:
    return locale_ctx.get()


TzDep = Annotated[ZoneInfo, Depends(request_timezone)]
TzNameDep = Annotated[str, Depends(timezone_name)]
LocaleDep = Annotated[str, Depends(request_locale)]
TimezoneHeader = Annotated[str | None, Header(alias="X-Timezone", max_length=64)]
