"""FastAPI dependency'lari: container, autentifikatsiya, qurilma imzosi, use-case fabrikalari."""

from typing import Annotated

from fastapi import Depends, Header, Request

from app.application.auth.dto import AuthContext
from app.application.auth.sessions import Authenticate
from app.application.auth.tokens import TokenIssuer
from app.application.common.device_proof import DeviceProof
from app.application.common.rate_limit import MINUTE, Limit
from app.container import Container
from app.domain.common.errors import AuthenticationError, InvalidDeviceSignatureError


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
IdempotencyKey = Annotated[str | None, Header(alias="Idempotency-Key")]
