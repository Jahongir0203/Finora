from fastapi import APIRouter, Request, status

from app.application.auth.dto import PinFailuresCommand
from app.application.auth.sessions import ReportPinFailures
from app.application.notifications.use_cases import NotificationService
from app.presentation.api.deps import AuthDep, ContainerDep, DeviceProofDep, client_ip
from app.presentation.schemas.auth import RefreshIn
from app.presentation.schemas.common import ERROR_RESPONSES
from app.presentation.schemas.notifications import PushTokenIn

router = APIRouter(prefix="/devices/current", tags=["devices"], responses=ERROR_RESPONSES)


@router.post("/push-token", status_code=status.HTTP_204_NO_CONTENT)
async def register_push_token(body: PushTokenIn, ctx: AuthDep, c: ContainerDep) -> None:
    """Token faqat joriy qurilmaga yoziladi; logout'da o'chiriladi (BE-404)."""
    await NotificationService(c.uow(), c.clock).register_push_token(ctx, body.provider,
                                                                    body.token)


@router.delete("/push-token", status_code=status.HTTP_204_NO_CONTENT)
async def remove_push_token(ctx: AuthDep, c: ContainerDep) -> None:
    await NotificationService(c.uow(), c.clock).remove_push_token(ctx)


@router.post("/pin-lockout", status_code=status.HTTP_204_NO_CONTENT)
async def pin_lockout(body: RefreshIn, proof: DeviceProofDep, request: Request,
                      c: ContainerDep) -> None:
    """5 marta xato PIN (BE-202). Qurilma kaliti bilan imzolangan bo'lishi shart —
    imzosiz so'rov 401. Shu qurilma sessiyasi bekor qilinadi."""
    await ReportPinFailures(c.uow(), c.hasher, c.key_verifier, c.notifier, c.clock,
                            c.settings).execute(
        PinFailuresCommand(refresh_token=body.refresh_token, proof=proof, ip=client_ip(request))
    )
