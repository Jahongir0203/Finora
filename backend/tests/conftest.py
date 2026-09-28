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

from app.container import Container
from app.core.config import Settings
from app.infrastructure.cache.memory import InMemoryKeyValueStore
from app.infrastructure.clock import SystemClock
from app.infrastructure.db.base import Base
from app.infrastructure.db.session import create_engine, create_session_factory
from app.infrastructure.notifications.log_notifier import LogNotifier
from app.infrastructure.security.cipher import AesGcmPhoneCipher
from app.infrastructure.security.device_keys import EcdsaP256Verifier
from app.infrastructure.security.hashing import HmacHasher
from app.infrastructure.security.jwt_tokens import Es256AccessTokenService
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


@pytest.fixture
async def container(settings: Settings) -> AsyncIterator[Container]:
    engine = create_engine(settings)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    c = Container(
        settings=settings,
        engine=engine,
        session_factory=create_session_factory(engine),
        kv=InMemoryKeyValueStore(),
        clock=SystemClock(),
        hasher=HmacHasher(settings),
        cipher=AesGcmPhoneCipher(settings),
        access_tokens=Es256AccessTokenService(settings),
        key_verifier=EcdsaP256Verifier(),
        sms=InMemorySmsSender(),
        notifier=LogNotifier(),
        storage=LocalFileStorage(settings.storage_dir),
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
                          json={"phone": phone, "installation_id": device.installation_id})
    assert r.status_code == 202, r.text
    r = await client.post("/v1/auth/verify", json={
        "phone": phone, "code": last_code(container),
        "installation_id": device.installation_id, "device_public_key": device.public_b64,
        "device_name": "Test phone", "platform": "ios", **extra,
    })
    assert r.status_code == 200, r.text
    body = r.json()
    return LoggedIn(body["access_token"], body["refresh_token"], device, phone)


def idem() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid.uuid4())}
