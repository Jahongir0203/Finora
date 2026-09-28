"""Alembic muhiti. URL FINORA_MIGRATIONS_DATABASE_URL'dan (owner roli) olinadi.

Ilova roli (finora_app) DDL huquqiga ega emas — migratsiyalar faqat owner bilan
(02-backend.md, 5-bo'lim: ilova xizmati DROP / ALTER qila olmaydi).
"""

import asyncio
import os
from typing import Any

from alembic import context
from sqlalchemy import DateTime
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.infrastructure.db import models  # noqa: F401 — jadvallar metadata'ga yozilsin
from app.infrastructure.db.base import Base, UTCDateTime

target_metadata = Base.metadata


def _url() -> str:
    url = os.environ.get("FINORA_MIGRATIONS_DATABASE_URL")
    if not url:
        raise RuntimeError("FINORA_MIGRATIONS_DATABASE_URL o'rnatilmagan (owner roli)")
    return url


def _render_item(type_: str, obj: Any, autogen_context: Any) -> str | bool:
    # Migratsiya fayllari ilova kodiga bog'lanmasin — UTCDateTime oddiy timestamptz
    if type_ == "type" and isinstance(obj, UTCDateTime):
        return repr(DateTime(timezone=True)).replace("DateTime", "sa.DateTime")
    return False


def _configure(connection: Connection | None = None, **kw: Any) -> None:
    context.configure(connection=connection, target_metadata=target_metadata,
                      render_item=_render_item, compare_type=True, **kw)


def run_migrations_offline() -> None:
    _configure(url=_url(), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def _run_sync(connection: Connection) -> None:
    _configure(connection)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(_url())
    async with engine.connect() as conn:
        await conn.run_sync(_run_sync)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
