"""Telegram bot — polling rejimi (lokal dev uchun: webhook va HTTPS domen kerak emas).

    uv run python -m app.telegram_poll

Server (API) alohida ishlaydi; bu jarayon Telegram'dan yangi xabarlarni o'zi so'rab oladi va
ularni webhook bilan bir xil ishlovchiga (TelegramWebhook) beradi. Ishga tushganda webhook
o'chiriladi (Telegram ikkalasini birga qo'llamaydi).

Prod'da webhook tavsiya etiladi (`app.telegram_setup`): polling faqat BITTA nusxada ishlashi
mumkin — ikki jarayon bir vaqtda getUpdates qilsa Telegram 409 qaytaradi.
"""

import asyncio
import logging

from app.application.common.interfaces import TelegramChatUnavailable
from app.application.telegram.use_cases import TelegramWebhook
from app.container import Container, build_container
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.domain.common.errors import ServiceUnavailableError
from app.infrastructure.telegram.bot import TelegramBotClient

logger = logging.getLogger("finora.telegram")

POLL_TIMEOUT_SECONDS = 25
RETRY_DELAY_SECONDS = 3.0


async def poll(container: Container, bot: TelegramBotClient, *,
               max_rounds: int | None = None) -> int:
    """Update'larni o'qib qayta ishlaydi. max_rounds — testlar uchun. Qaytaradi: nechta update."""
    handler = TelegramWebhook(container.uow, bot, container.hasher, container.clock)
    await bot.delete_webhook()
    offset: int | None = None
    handled = rounds = 0
    while max_rounds is None or rounds < max_rounds:
        rounds += 1
        try:
            updates = await bot.get_updates(offset, POLL_TIMEOUT_SECONDS)
        except (ServiceUnavailableError, TelegramChatUnavailable):
            logger.warning("telegram_poll_failed")
            await asyncio.sleep(RETRY_DELAY_SECONDS)
            continue
        for update in updates:
            update_id = update.get("update_id")
            if isinstance(update_id, int):
                offset = update_id + 1  # tasdiqlash: keyingi so'rovda qayta kelmaydi
            try:
                await handler.handle(update)
                handled += 1
            except Exception:
                # Bitta buzilgan update butun botni to'xtatmasin
                logger.exception("telegram_update_failed")
    return handled


async def _main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    if settings.telegram_bot_token is None:
        raise SystemExit("FINORA_TELEGRAM_BOT_TOKEN kerak")
    container = build_container(settings)
    bot = TelegramBotClient(settings.telegram_bot_token.get_secret_value())
    logger.info("telegram_polling_started")
    try:
        await poll(container, bot)
    finally:
        await bot.aclose()
        await container.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
