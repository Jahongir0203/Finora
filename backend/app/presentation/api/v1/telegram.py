import hmac
from typing import Annotated, Any

from fastapi import APIRouter, Header, Request, Response

from app.application.telegram.use_cases import TelegramWebhook
from app.domain.common.errors import NotFoundError
from app.presentation.api.deps import ContainerDep

router = APIRouter(prefix="/telegram", tags=["telegram"], include_in_schema=False)


@router.post("/webhook")
async def telegram_webhook(
    request: Request, c: ContainerDep,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header(max_length=256)] = None,
) -> Response:
    """Faqat Telegram chaqiradi: setWebhook'dagi secret_token sarlavhada keladi.
    Bot sozlanmagan yoki secret noto'g'ri — 404 (endpoint borligi oshkor bo'lmaydi)."""
    secret = c.settings.telegram_webhook_secret
    given = (x_telegram_bot_api_secret_token or "").encode()
    if c.telegram is None or secret is None or not hmac.compare_digest(
            given, secret.get_secret_value().encode()):
        raise NotFoundError()
    try:
        update: Any = await request.json()
    except ValueError:
        return Response(status_code=200)
    if isinstance(update, dict):
        await TelegramWebhook(c.uow, c.telegram, c.hasher, c.clock).handle(update)
    # Telegram 200 bo'lmasa qayta yuboradi — ishlov natijasidan qat'i nazar 200
    return Response(status_code=200)
