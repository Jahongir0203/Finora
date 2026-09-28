"""Composition root: barcha adapterlar shu yerda yig'iladi (DI)."""

from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.common.interfaces import (
    AccessTokenService,
    Clock,
    DeviceKeyVerifier,
    FileStorage,
    KeyValueStore,
    Notifier,
    PhoneCipher,
    SecretHasher,
    SmsSender,
)
from app.application.common.rate_limit import RateLimiter
from app.core.config import Environment, Settings
from app.infrastructure.cache.memory import InMemoryKeyValueStore
from app.infrastructure.clock import SystemClock
from app.infrastructure.db.session import create_engine, create_session_factory
from app.infrastructure.db.uow import SqlAlchemyUnitOfWork
from app.infrastructure.notifications.log_notifier import LogNotifier
from app.infrastructure.security.cipher import AesGcmPhoneCipher
from app.infrastructure.security.device_keys import EcdsaP256Verifier
from app.infrastructure.security.hashing import HmacHasher
from app.infrastructure.security.jwt_tokens import Es256AccessTokenService
from app.infrastructure.sms.console import ConsoleSmsSender
from app.infrastructure.storage.local import LocalFileStorage


@dataclass
class Container:
    settings: Settings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    kv: KeyValueStore
    clock: Clock
    hasher: SecretHasher
    cipher: PhoneCipher
    access_tokens: AccessTokenService
    key_verifier: DeviceKeyVerifier
    sms: SmsSender
    notifier: Notifier
    storage: FileStorage
    limiter: RateLimiter = field(init=False)

    def __post_init__(self) -> None:
        self.limiter = RateLimiter(self.kv)

    def uow(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_factory)


def _build_kv(settings: Settings) -> KeyValueStore:
    if settings.redis_url:
        from redis.asyncio import Redis

        from app.infrastructure.cache.redis_store import RedisKeyValueStore

        return RedisKeyValueStore(Redis.from_url(settings.redis_url))
    if settings.env is Environment.PROD:
        raise RuntimeError("Prod'da Redis majburiy (rate limit bir nechta instansiya uchun)")
    return InMemoryKeyValueStore()


def build_container(settings: Settings) -> Container:
    engine = create_engine(settings)
    return Container(
        settings=settings,
        engine=engine,
        session_factory=create_session_factory(engine),
        kv=_build_kv(settings),
        clock=SystemClock(),
        hasher=HmacHasher(settings),
        cipher=AesGcmPhoneCipher(settings),
        access_tokens=Es256AccessTokenService(settings),
        key_verifier=EcdsaP256Verifier(),
        # TODO: prod uchun real SMS provayder adapteri (Eskiz/Playmobile) — shu port orqali
        sms=ConsoleSmsSender(settings),
        notifier=LogNotifier(),
        storage=LocalFileStorage(settings.storage_dir),
    )
