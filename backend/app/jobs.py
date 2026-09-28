"""Davriy tozalash vazifalari. Cron/Kubernetes CronJob har soatda ishga tushiradi:

    uv run python -m app.jobs purge

- Muddati o'tgan yoki yuklab olingan eksport fayllari (02-backend.md, 6-bo'lim: 24 soat).
- 24 soatdan eski Idempotency-Key yozuvlari (4-bo'lim).
"""

import argparse
import asyncio
import logging
from datetime import timedelta

from app.application.exports.use_cases import ExportService
from app.container import Container, build_container
from app.core.config import get_settings
from app.core.logging import configure_logging

logger = logging.getLogger("finora.jobs")


async def purge(container: Container) -> dict[str, int]:
    exports = await ExportService(
        container.uow(), container.storage, container.hasher, container.limiter,
        container.clock, container.settings,
    ).purge_expired()
    cutoff = container.clock.now() - timedelta(seconds=container.settings.idempotency_ttl_seconds)
    async with container.uow() as uow:
        keys = await uow.idempotency.purge_older_than(cutoff)
        await uow.commit()
    result = {"exports": exports, "idempotency_keys": keys}
    logger.info("purge_done", extra={"purged": result})
    return result


async def _main(command: str) -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    container = build_container(settings)
    try:
        if command == "purge":
            await purge(container)
    finally:
        await container.aclose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="python -m app.jobs")
    parser.add_argument("command", choices=["purge"])
    asyncio.run(_main(parser.parse_args().command))
