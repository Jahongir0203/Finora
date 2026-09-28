from redis.asyncio import Redis

_INCR_LUA = """
local v = redis.call('INCR', KEYS[1])
if v == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
local ttl = redis.call('TTL', KEYS[1])
return {v, ttl}
"""


class RedisKeyValueStore:
    def __init__(self, client: Redis) -> None:
        self._r = client
        self._incr = client.register_script(_INCR_LUA)

    async def get(self, key: str) -> str | None:
        value = await self._r.get(key)
        return value.decode() if isinstance(value, bytes) else value

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._r.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> bool:
        return bool(await self._r.delete(key))

    async def incr(self, key: str, ttl_seconds: int) -> tuple[int, int]:
        value, ttl = await self._incr(keys=[key], args=[ttl_seconds])
        return int(value), max(1, int(ttl))

    async def ttl(self, key: str) -> int:
        return max(0, int(await self._r.ttl(key)))
