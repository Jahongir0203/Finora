import base64
import hashlib
import re
import time
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.application.common.interfaces import PushSendResult
from app.application.notifications.notifier import AppNotifier
from app.container import Container
from app.core.config import Settings
from app.infrastructure.ai.local import RuleBasedInsightsModel
from app.infrastructure.cache.memory import InMemoryKeyValueStore
from app.infrastructure.clock import SystemClock
from app.infrastructure.db.base import Base
from app.infrastructure.db.session import create_engine, create_session_factory
from app.infrastructure.db.uow import SqlAlchemyUnitOfWork
from app.infrastructure.files.antivirus import NoopScanner
from app.infrastructure.files.images import PillowImageSanitizer
from app.infrastructure.security.cipher import AesGcmPhoneCipher
from app.infrastructure.security.device_keys import EcdsaP256Verifier
from app.infrastructure.security.hashing import HmacHasher
from app.infrastructure.security.jwt_tokens import Es256AccessTokenService
from app.infrastructure.security.url_signer import HmacUrlSigner
from app.infrastructure.sms.console import InMemorySmsSender
from app.infrastructure.storage.local import LocalFileStorage
from app.main import create_app


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        env="test",
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'test.db'}",
        redis_url=None,
        storage_dir=str(tmp_path / "storage"),
        log_level="INFO",
    )


class FakePush:
    """Push provayderi o'rnida: yuborilganlarni yig'adi, `invalid` tokenlar uchun 410 beradi."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []
        self.invalid: set[str] = set()
        self.fail = False

    async def send(self, provider, token: str, title: str, body: str) -> PushSendResult:
        if self.fail:
            return PushSendResult.FAILED
        if token in self.invalid:
            return PushSendResult.INVALID_TOKEN
        self.sent.append((token, title, body))
        return PushSendResult.OK


@pytest.fixture
async def container(settings: Settings) -> AsyncIterator[Container]:
    engine = create_engine(settings)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = create_session_factory(engine)
    clock = SystemClock()
    push = FakePush()
    c = Container(
        settings=settings,
        engine=engine,
        session_factory=session_factory,
        kv=InMemoryKeyValueStore(),
        clock=clock,
        hasher=HmacHasher(settings),
        cipher=AesGcmPhoneCipher(settings),
        access_tokens=Es256AccessTokenService(settings),
        key_verifier=EcdsaP256Verifier(),
        sms=InMemorySmsSender(),
        notifier=AppNotifier(lambda: SqlAlchemyUnitOfWork(session_factory), push, clock),
        storage=LocalFileStorage(settings.storage_dir),
        scanner=NoopScanner(settings),
        sanitizer=PillowImageSanitizer(settings.max_image_pixels),
        signer=HmacUrlSigner(settings),
        insights=RuleBasedInsightsModel(),
        push=push,
        ocr=FakeOcr(),
    )
    yield c
    await engine.dispose()


@pytest.fixture
async def client(settings: Settings, container: Container) -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(settings, container)
    transport = httpx.ASGITransport(app=app, client=("10.0.0.1", 1234))
    async with httpx.AsyncClient(transport=transport, base_url="https://api.test") as c:
        yield c


@dataclass
class DeviceKey:
    """Mobil qurilmadagi Secure Enclave / Keystore kalitini simulyatsiya qiladi."""

    installation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    private: ec.EllipticCurvePrivateKey = field(
        default_factory=lambda: ec.generate_private_key(ec.SECP256R1())
    )

    @property
    def public_b64(self) -> str:
        der = self.private.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return base64.urlsafe_b64encode(der).decode()

    def sign(self, method: str, path: str, body: bytes, ts: int | None = None) -> dict[str, str]:
        ts = ts if ts is not None else int(time.time())
        msg = f"{method}\n{path}\n{ts}\n{hashlib.sha256(body).hexdigest()}".encode()
        sig = self.private.sign(msg, ec.ECDSA(hashes.SHA256()))
        return {"X-Device-Timestamp": str(ts),
                "X-Device-Signature": base64.urlsafe_b64encode(sig).decode().rstrip("=")}


@dataclass
class LoggedIn:
    access: str
    refresh: str
    device: DeviceKey
    phone: str
    user: dict = field(default_factory=dict)

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access}"}


def last_code(container: Container) -> str:
    sms: InMemorySmsSender = container.sms  # type: ignore[assignment]
    match = re.search(r"\b(\d{6})\b", sms.outbox[-1][1])
    assert match
    return match.group(1)


async def login(client: httpx.AsyncClient, container: Container, phone: str,
                device: DeviceKey | None = None, **extra: object) -> LoggedIn:
    device = device or DeviceKey()
    r = await client.post("/v1/auth/otp",
                          json={"phone": phone, "device_id": device.installation_id})
    assert r.status_code == 200, r.text
    r = await client.post("/v1/auth/verify", json={
        "phone": phone, "code": last_code(container),
        "device_id": device.installation_id, "device_public_key": device.public_b64,
        "device_name": "Test phone", "platform": "ios", **extra,
    })
    assert r.status_code == 200, r.text
    # Keyingi login shu raqam bilan 60 s qayta yuborish limitiga tushmasin — vaqtni "suramiz"
    if isinstance(container.kv, InMemoryKeyValueStore):
        container.kv.time_offset += container.settings.otp_resend_seconds + 1
    body = r.json()
    return LoggedIn(body["access_token"], body["refresh_token"], device, phone, body["user"])


def idem() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid.uuid4())}


async def expense(client: httpx.AsyncClient, s: LoggedIn, amount: int = 50_000,
                  category_id: str = "food", **extra: object) -> dict:
    r = await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "type": "expense", "amount": amount, "category_id": category_id, **extra})
    assert r.status_code == 201, r.text
    return r.json()["transaction"]


async def income(client: httpx.AsyncClient, s: LoggedIn, amount: int = 1_000_000,
                 **extra: object) -> dict:
    r = await client.post("/v1/transactions", headers={**s.headers, **idem()}, json={
        "type": "income", "amount": amount, "category_id": "salary", **extra})
    assert r.status_code == 201, r.text
    return r.json()["transaction"]


class FakeOcr:
    """OCR provayderi o'rnida: `result` ni qaytaradi (None — o'qib bo'lmadi)."""

    def __init__(self) -> None:
        from app.domain.receipts.entities import ParsedReceipt, ReceiptItem

        self.result: ParsedReceipt | None = ParsedReceipt(
            merchant="Korzinka Chilonzor", total=86_500, occurred_at=None,
            items=[ReceiptItem("Non", 2, 5_000), ReceiptItem("Sut", 1, 14_500)],
            confidence=0.93)

    async def read(self, image: bytes):
        return self.result


async def delete_account(client: httpx.AsyncClient, container: Container, s: LoggedIn) -> None:
    """BE-1304: SMS kod bilan tasdiqlangan o'chirish."""
    if isinstance(container.kv, InMemoryKeyValueStore):
        container.kv.time_offset += container.settings.otp_resend_seconds + 1
    r = await client.post("/v1/me/delete-code", headers=s.headers)
    assert r.status_code == 200, r.text
    r = await client.request("DELETE", "/v1/me", headers=s.headers,
                             json={"code": last_code(container)})
    assert r.status_code == 204, r.text
