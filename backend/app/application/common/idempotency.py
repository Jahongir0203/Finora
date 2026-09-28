"""Idempotency-Key (02-backend.md, 4-bo'lim).

Yozuv yaratuvchi so'rov natijasi kalit bilan birga, aynan o'sha tranzaksiyada
saqlanadi. Takroriy so'rov yangi yozuv yaratmaydi — saqlangan javob qaytadi.
"""

import hashlib
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID

from app.domain.common.errors import (
    IdempotencyConflictError,
    IdempotencyKeyRequiredError,
    ValidationFailedError,
)

if TYPE_CHECKING:
    from app.application.common.uow import UnitOfWork

MAX_KEY_LENGTH = 128


@dataclass(slots=True)
class IdempotencyRecord:
    user_id: UUID
    key: str
    fingerprint: str
    response: dict[str, Any]
    created_at: datetime


class IdempotencyConflict(Exception):  # noqa: N818 — infratuzilma signali
    """Parallel so'rov shu kalitni birinchi bo'lib yozdi (unique constraint)."""


class IdempotencyRepository(Protocol):
    async def get(self, user_id: UUID, key: str) -> IdempotencyRecord | None: ...
    async def delete_stale(self, user_id: UUID, key: str, before: datetime) -> None: ...
    async def reserve(self, record: IdempotencyRecord) -> None:
        """Kalitni darhol (flush) yozadi. Band bo'lsa IdempotencyConflict.
        Postgres'da parallel dublikat shu yerda birinchisi commit bo'lguncha kutadi."""
        ...
    async def set_response(self, user_id: UUID, key: str, response: dict[str, Any]) -> None: ...
    async def purge_older_than(self, before: datetime) -> int: ...


def fingerprint(operation: str, payload: dict[str, Any]) -> str:
    raw = json.dumps({"op": operation, "payload": payload}, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def validate_key(key: str | None) -> str:
    if key is None or not key.strip():
        raise IdempotencyKeyRequiredError()
    key = key.strip()
    if len(key) > MAX_KEY_LENGTH or not key.isprintable():
        raise ValidationFailedError("Idempotency-Key noto'g'ri")
    return key


def _replay(existing: IdempotencyRecord | None, fp: str) -> dict[str, Any]:
    if existing is None or existing.fingerprint != fp:
        raise IdempotencyConflictError()
    return existing.response


async def run_idempotent(
    uow: "UnitOfWork",
    *,
    user_id: UUID,
    key: str | None,
    operation: str,
    payload: dict[str, Any],
    now: datetime,
    ttl_seconds: int,
    action: Callable[[], Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    """Kalit + natija bitta DB tranzaksiyasida saqlanadi (kalit 24 soat amal qiladi)."""
    key = validate_key(key)
    fp = fingerprint(operation, payload)

    await uow.idempotency.delete_stale(user_id, key, now - timedelta(seconds=ttl_seconds))
    existing = await uow.idempotency.get(user_id, key)
    if existing is not None:
        return _replay(existing, fp)

    try:
        await uow.idempotency.reserve(
            IdempotencyRecord(user_id=user_id, key=key, fingerprint=fp, response={}, created_at=now)
        )
    except IdempotencyConflict:
        await uow.rollback()
        return _replay(await uow.idempotency.get(user_id, key), fp)

    response = await action()
    await uow.idempotency.set_response(user_id, key, response)
    await uow.commit()
    return response
