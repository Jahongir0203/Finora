"""Xotiradagi KeyValueStore — faqat test va lokal dev uchun (bitta jarayon)."""

import asyncio
import time


class InMemoryKeyValueStore:
    def __init__(self) -> None:
        self._data: dict[str, tuple[str, float]] = {}
        self._lock = asyncio.Lock()
        self.time_offset = 0.0  # testlarda vaqtni "surish" uchun

    def _now(self) -> float:
        return time.monotonic() + self.time_offset

    def _alive(self, key: str) -> tuple[str, float] | None:
        item = self._data.get(key)
        if item is None:
            return None
        if item[1] <= self._now():
            del self._data[key]
            return None
        return item

    async def get(self, key: str) -> str | None:
        item = self._alive(key)
        return item[0] if item else None

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._data[key] = (value, self._now() + ttl_seconds)

    async def delete(self, key: str) -> bool:
        async with self._lock:
            if self._alive(key) is None:
                return False
            del self._data[key]
            return True

    async def incr(self, key: str, ttl_seconds: int) -> tuple[int, int]:
        async with self._lock:
            item = self._alive(key)
            if item is None:
                self._data[key] = ("1", self._now() + ttl_seconds)
                return 1, ttl_seconds
            value = int(item[0]) + 1
            self._data[key] = (str(value), item[1])
            return value, max(1, int(item[1] - self._now()))

    async def ttl(self, key: str) -> int:
        item = self._alive(key)
        return max(1, int(item[1] - self._now())) if item else 0
