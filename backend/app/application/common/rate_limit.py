"""Fixed-window rate limiter (02-backend.md, 4-bo'lim jadvali)."""

from collections.abc import Iterable
from dataclasses import dataclass

from app.application.common.interfaces import KeyValueStore
from app.domain.common.errors import RateLimitedError

MINUTE = 60
HOUR = 3600
DAY = 86400


@dataclass(frozen=True, slots=True)
class Limit:
    name: str
    max_hits: int
    window_seconds: int


class RateLimiter:
    def __init__(self, store: KeyValueStore) -> None:
        self._store = store

    async def hit(self, scope: str, subject: str, limits: Iterable[Limit]) -> None:
        """Har bir limit uchun hisoblagichni oshiradi. Birortasi oshsa — RateLimitedError."""
        for limit in limits:
            key = f"rl:{scope}:{limit.name}:{subject}"
            count, ttl = await self._store.incr(key, limit.window_seconds)
            if count > limit.max_hits:
                raise RateLimitedError(retry_after=ttl or limit.window_seconds)

    async def hit_many(self, scope: str, subjects: Iterable[str], limits: list[Limit]) -> None:
        """Bir nechta kalit (telefon, IP, qurilma) bo'yicha alohida hisoblash."""
        for subject in subjects:
            await self.hit(scope, subject, limits)
