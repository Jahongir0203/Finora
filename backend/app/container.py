"""Composition root: barcha adapterlar shu yerda yig'iladi (DI)."""

from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.common.interfaces import (
    AccessTokenService,
    Clock,
    DeviceKeyVerifier,
    FileStorage,
    ImageSanitizer,
    InsightsModel,
    KeyValueStore,
    MalwareScanner,
    Notifier,
    PhoneCipher,
    PushSender,
    SecretHasher,
    SmsSender,
    UrlSigner,
)
from app.application.common.rate_limit import RateLimiter
from app.application.notifications.notifier import AppNotifier
from app.core.config import Environment, Settings, SmsProvider
from app.domain.notifications.entities import PushProvider
from app.infrastructure.ai.local import RuleBasedInsightsModel
from app.infrastructure.cache.memory import InMemoryKeyValueStore
from app.infrastructure.clock import SystemClock
from app.infrastructure.db.session import create_engine, create_session_factory
from app.infrastructure.db.uow import SqlAlchemyUnitOfWork
from app.infrastructure.files.antivirus import ClamAvScanner, NoopScanner
from app.infrastructure.files.images import PillowImageSanitizer
from app.infrastructure.push.apns import ApnsSender
from app.infrastructure.push.fcm import FcmSender
from app.infrastructure.push.router import RoutingPushSender
from app.infrastructure.security.cipher import AesGcmPhoneCipher
from app.infrastructure.security.device_keys import EcdsaP256Verifier
from app.infrastructure.security.hashing import HmacHasher
from app.infrastructure.security.jwt_tokens import Es256AccessTokenService
from app.infrastructure.security.url_signer import HmacUrlSigner
from app.infrastructure.sms.console import ConsoleSmsSender
from app.infrastructure.sms.eskiz import EskizSmsSender
from app.infrastructure.storage.local import LocalFileStorage
from app.infrastructure.storage.s3 import S3FileStorage


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
    scanner: MalwareScanner
    sanitizer: ImageSanitizer
    signer: UrlSigner
    insights: InsightsModel
    push: PushSender | None = None
    limiter: RateLimiter = field(init=False)

    def __post_init__(self) -> None:
        self.limiter = RateLimiter(self.kv)

    def uow(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_factory)

    async def aclose(self) -> None:
        """HTTP klientlari (SMS, push) va DB pulini yopadi."""
        for resource in (self.sms, self.push):
            close = getattr(resource, "aclose", None)
            if close is not None:
                await close()
        await self.engine.dispose()


def _build_kv(settings: Settings) -> KeyValueStore:
    if settings.redis_url:
        from redis.asyncio import Redis

        from app.infrastructure.cache.redis_store import RedisKeyValueStore

        return RedisKeyValueStore(Redis.from_url(settings.redis_url))
    if settings.env is Environment.PROD:
        raise RuntimeError("Prod'da Redis majburiy (rate limit bir nechta instansiya uchun)")
    return InMemoryKeyValueStore()


def _build_scanner(settings: Settings) -> MalwareScanner:
    if settings.clamav_host:
        return ClamAvScanner(settings.clamav_host, settings.clamav_port)
    return NoopScanner(settings)


def _build_sms(settings: Settings) -> SmsSender:
    if settings.sms_provider is SmsProvider.ESKIZ:
        return EskizSmsSender(settings)
    return ConsoleSmsSender(settings)


def _build_push(settings: Settings) -> PushSender | None:
    senders: dict[PushProvider, PushSender] = {}
    if settings.fcm_service_account_json:
        senders[PushProvider.FCM] = FcmSender(settings.fcm_service_account_json.get_secret_value())
    if settings.apns_configured:
        assert settings.apns_private_key and settings.apns_team_id
        assert settings.apns_key_id and settings.apns_bundle_id
        senders[PushProvider.APNS] = ApnsSender(
            settings.apns_team_id, settings.apns_key_id,
            settings.apns_private_key.get_secret_value(), settings.apns_bundle_id,
            sandbox=settings.apns_sandbox,
        )
    return RoutingPushSender(senders) if senders else None


def _build_storage(settings: Settings) -> FileStorage:
    if settings.s3_bucket:
        return S3FileStorage(settings)
    return LocalFileStorage(settings.storage_dir)


def build_container(settings: Settings) -> Container:
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    clock = SystemClock()
    push = _build_push(settings)
    return Container(
        settings=settings,
        engine=engine,
        session_factory=session_factory,
        kv=_build_kv(settings),
        clock=clock,
        hasher=HmacHasher(settings),
        cipher=AesGcmPhoneCipher(settings),
        access_tokens=Es256AccessTokenService(settings),
        key_verifier=EcdsaP256Verifier(),
        sms=_build_sms(settings),
        notifier=AppNotifier(lambda: SqlAlchemyUnitOfWork(session_factory), push, clock),
        storage=_build_storage(settings),
        scanner=_build_scanner(settings),
        sanitizer=PillowImageSanitizer(settings.max_image_pixels),
        signer=HmacUrlSigner(settings),
        # TODO: tashqi LLM — faqat "o'qitishda ishlatmaslik" shartnomasidan keyin (8-bo'lim)
        insights=RuleBasedInsightsModel(),
        push=push,
    )
