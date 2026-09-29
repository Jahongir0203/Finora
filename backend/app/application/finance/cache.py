"""Agregatlar keshi (BE-505): Redis'da, user bo'yicha versiya kaliti bilan invalidatsiya.

Har qanday pul harakati (tranzaksiya, hisob, goal yozuvi) `invalidate()` chaqiradi — versiya
oshadi va eski kesh kalitlari o'z-o'zidan eskiradi (TTL). O'qishda kesh bo'lmasa — DB.
"""

import json
from typing import Any
from uuid import UUID

from app.application.common.interfaces import KeyValueStore

CACHE_TTL_SECONDS = 300
_VERSION_TTL_SECONDS = 30 * 24 * 3600


class AggregateCache:
    def __init__(self, kv: KeyValueStore, ttl_seconds: int = CACHE_TTL_SECONDS) -> None:
        self._kv = kv
        self._ttl = ttl_seconds

    async def _version(self, user_id: UUID) -> str:
        return await self._kv.get(f"agg:v:{user_id}") or "0"

    async def get(self, user_id: UUID, name: str) -> Any | None:
        raw = await self._kv.get(f"agg:{user_id}:{await self._version(user_id)}:{name}")
        return json.loads(raw) if raw is not None else None

    async def set(self, user_id: UUID, name: str, value: Any) -> None:
        key = f"agg:{user_id}:{await self._version(user_id)}:{name}"
        await self._kv.set(key, json.dumps(value), self._ttl)

    async def invalidate(self, user_id: UUID) -> None:
        await self._kv.incr(f"agg:v:{user_id}", _VERSION_TTL_SECONDS)
