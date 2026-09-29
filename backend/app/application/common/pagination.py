"""Cursor pagination: `?cursor=&limit=` (standart 30, maksimum 100).

Cursor — oxirgi elementning tartiblash kaliti (vaqt + UUIDv7), base64url JSON. Mijoz uchun
shaffof emas; buzilgan cursor — 422.
"""

import base64
import binascii
import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.common.errors import ValidationFailedError

DEFAULT_LIMIT = 30
MAX_LIMIT = 100

@dataclass(frozen=True, slots=True)
class Cursor:
    at: datetime
    id: UUID


@dataclass(frozen=True, slots=True)
class Page[T]:
    items: list[T]
    next_cursor: str | None


def encode_cursor(at: datetime, item_id: UUID) -> str:
    raw = json.dumps([at.isoformat(), str(item_id)], separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(value: str | None) -> Cursor | None:
    if not value:
        return None
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        at, item_id = json.loads(raw)
        parsed = datetime.fromisoformat(at)
        if parsed.tzinfo is None:
            raise ValueError
        return Cursor(parsed, UUID(item_id))
    except (binascii.Error, ValueError, TypeError, json.JSONDecodeError):
        raise ValidationFailedError("cursor noto'g'ri", fields=["cursor"]) from None


def clamp_limit(limit: int | None) -> int:
    return max(1, min(limit or DEFAULT_LIMIT, MAX_LIMIT))
