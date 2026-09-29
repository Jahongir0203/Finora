"""Davriy vazifalar (scheduler). Kubernetes CronJob / cron:

    uv run python -m app.jobs tick        # har soat: quyidagilarning hammasi (idempotent)
    uv run python -m app.jobs <buyruq>    # alohida

- purge     — muddati o'tgan eksportlar (24 soat), 24 soatdan eski Idempotency-Key'lar,
              tasdiqlanmagan cheklar (24 soat) — 02-backend.md 4, 6; BE-703.
- exports   — uzilib qolgan `pending` eksportlarni qayta ishlash (BE-602).
- push      — yuborilmagan push'larni qayta urinish (BE-404).
- reminders — sanalarni surish + payment_due (BE-1202, BE-403).
- weekly    — haftalik hisobot, dushanba 09:00 (BE-403).
- autosave  — goal auto-save (BE-1105).
- insights  — tavsiya detektorlari (BE-901), kechasi.
- rates     — CBU valyuta kurslari (BE-1602), kuniga bir marta.
- reencrypt-phones — kalit almashtirishdan keyin telefonlarni yangi kalitga o'tkazish.
- audit-retention — 1 yildan eski audit yozuvlari (FINORA_MAINTENANCE_DATABASE_URL,
              ya'ni finora_owner roli bilan; ilova roli audit_log'dan o'chira olmaydi).
"""

import argparse
import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Any

from app.application.currencies.use_cases import RatesJob
from app.application.exports.use_cases import ExportService
from app.application.goals.use_cases import AutoSaveJob
from app.application.insights.use_cases import InsightService
from app.application.notifications.weekly import WeeklyReportJob, iter_users
from app.application.receipts.use_cases import ReceiptService
from app.application.reminders.use_cases import ReminderJob
from app.container import Container, build_container
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.domain.common.time import tz_or_default
from app.infrastructure.files.images import sniff_image_format

logger = logging.getLogger("finora.jobs")


def _exports(c: Container) -> ExportService:
    return ExportService(c.uow, c.storage, c.signer, c.limiter, c.clock, c.settings, c.renderers)


async def purge(c: Container) -> dict[str, int]:
    exports = await _exports(c).purge_expired()
    cutoff = c.clock.now() - timedelta(seconds=c.settings.idempotency_ttl_seconds)
    async with c.uow() as uow:
        keys = await uow.idempotency.purge_older_than(cutoff)
        await uow.commit()
    receipts = await ReceiptService(
        c.uow(), c.storage, c.scanner, c.sanitizer, c.signer, c.limiter, c.clock, c.settings,
        sniff_image_format).purge_unconfirmed()
    return {"exports": exports, "idempotency_keys": keys, "receipts": receipts}


async def exports(c: Container) -> dict[str, int]:
    return {"exports_processed": await _exports(c).process_stale()}


async def push(c: Container) -> dict[str, int]:
    return {"push_retried": await c.notifier.retry_pending()}


async def reminders(c: Container) -> dict[str, int]:
    return await ReminderJob(c.uow, c.clock, c.notifier).run()


async def weekly(c: Container) -> dict[str, int]:
    return {"weekly_sent": await WeeklyReportJob(c.uow, c.clock, c.notifier).run()}


async def autosave(c: Container) -> dict[str, int]:
    return await AutoSaveJob(c.uow, c.clock, c.ledger, c.notifier).run()


async def insights(c: Container) -> dict[str, int]:
    svc, n = InsightService(c.uow, c.kv, c.clock), 0
    async for user in iter_users(c.uow):
        try:
            await svc.compute(user.id, tz_or_default(user.timezone), force=True)
            n += 1
        except Exception:
            logger.exception("insights_failed")
    return {"insights_users": n}


async def rates(c: Container) -> dict[str, int]:
    if c.rates is None:
        return {"rates": 0}
    return {"rates": await RatesJob(c.uow(), c.rates, c.clock).run()}


async def reencrypt_phones(c: Container) -> dict[str, int]:
    """Kalit almashtirishdan keyin telefonlarni joriy kalit bilan qayta shifrlash (5-bo'lim)."""
    n = 0
    async for user in iter_users(c.uow):
        if not c.cipher.needs_rotation(user.phone_ciphertext):
            continue
        phone = c.cipher.decrypt(user.phone_ciphertext)
        async with c.uow() as uow:
            await uow.users.set_phone_ciphertext(user.id, c.cipher.encrypt(phone))
            await uow.commit()
        n += 1
    return {"reencrypted": n}


async def audit_retention(c: Container) -> dict[str, int]:
    secret = c.settings.maintenance_database_url
    if secret is None:
        logger.warning("audit_retention_skipped")
        return {"audit_deleted": 0}
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(secret.get_secret_value())
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text(
                "DELETE FROM audit_log WHERE created_at < now() - interval '1 year'"))
        return {"audit_deleted": result.rowcount or 0}
    finally:
        await engine.dispose()


COMMANDS: dict[str, Callable[[Container], Awaitable[dict[str, int]]]] = {
    "purge": purge, "exports": exports, "push": push, "reminders": reminders,
    "weekly": weekly, "autosave": autosave, "insights": insights, "rates": rates,
    "audit-retention": audit_retention, "reencrypt-phones": reencrypt_phones,
}
# Har soatlik "tick": arzon va idempotent vazifalar (insights/rates — alohida, kechasi)
TICK = ("purge", "exports", "push", "reminders", "weekly", "autosave")


async def run(container: Container, command: str) -> dict[str, Any]:
    names = TICK if command == "tick" else (command,)
    result: dict[str, Any] = {}
    for name in names:
        try:
            result.update(await COMMANDS[name](container))
        except Exception:
            logger.exception("job_failed", extra={"job": name})
            result[name] = "failed"
    logger.info("jobs_done", extra={"result": result})
    return result


async def _main(command: str) -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    container = build_container(settings)
    try:
        await run(container, command)
    finally:
        await container.aclose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="python -m app.jobs")
    parser.add_argument("command", choices=["tick", *COMMANDS])
    asyncio.run(_main(parser.parse_args().command))
