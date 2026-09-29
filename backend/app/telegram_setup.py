"""Telegram webhook'ni o'rnatish (bir marta, deploy'dan keyin):

    uv run python -m app.telegram_setup https://api.finora.uz/v1/telegram/webhook

Token va secret muhit o'zgaruvchilaridan (FINORA_TELEGRAM_BOT_TOKEN,
FINORA_TELEGRAM_WEBHOOK_SECRET). Telegram faqat HTTPS (443/80/88/8443) manzilga yuboradi.
"""

import argparse
import asyncio

from app.core.config import get_settings
from app.infrastructure.telegram.bot import TelegramBotClient


async def _main(url: str) -> None:
    s = get_settings()
    if s.telegram_bot_token is None or s.telegram_webhook_secret is None:
        raise SystemExit("FINORA_TELEGRAM_BOT_TOKEN va FINORA_TELEGRAM_WEBHOOK_SECRET kerak")
    if not url.startswith("https://"):
        raise SystemExit("Webhook manzili https:// bo'lishi kerak")
    bot = TelegramBotClient(s.telegram_bot_token.get_secret_value())
    try:
        await bot.set_webhook(url, s.telegram_webhook_secret.get_secret_value())
    finally:
        await bot.aclose()
    print("Webhook o'rnatildi")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="python -m app.telegram_setup")
    parser.add_argument("url")
    asyncio.run(_main(parser.parse_args().url))
