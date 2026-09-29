from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.auth.entities import Device, Platform, RefreshToken, RevokeReason, Session
from app.infrastructure.db.models import DeviceModel, RefreshTokenModel, SessionModel


def _device(m: DeviceModel) -> Device:
    return Device(id=m.id, user_id=m.user_id, installation_id=m.installation_id,
                  public_key=m.public_key, name=m.name, platform=Platform(m.platform),
                  created_at=m.created_at, last_seen_at=m.last_seen_at,
                  has_pin_setup=m.has_pin_setup, auto_lock_minutes=m.auto_lock_minutes,
                  biometric_enabled=m.biometric_enabled, city=m.city)


def _session(m: SessionModel) -> Session:
    return Session(id=m.id, user_id=m.user_id, device_id=m.device_id, created_at=m.created_at,
                   revoked_at=m.revoked_at,
                   revoke_reason=RevokeReason(m.revoke_reason) if m.revoke_reason else None)


class SqlDeviceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_for_user(self, user_id: UUID, device_id: UUID) -> Device | None:
        m = await self._s.scalar(
            select(DeviceModel).where(DeviceModel.id == device_id, DeviceModel.user_id == user_id)
        )
        return _device(m) if m else None

    async def get_by_installation(self, user_id: UUID, installation_id: UUID) -> Device | None:
        m = await self._s.scalar(
            select(DeviceModel).where(DeviceModel.user_id == user_id,
                                      DeviceModel.installation_id == installation_id)
        )
        return _device(m) if m else None

    async def list_for_user(self, user_id: UUID) -> list[Device]:
        rows = await self._s.scalars(
            select(DeviceModel).where(DeviceModel.user_id == user_id)
            .order_by(DeviceModel.last_seen_at.desc())
        )
        return [_device(m) for m in rows]

    async def add(self, device: Device) -> None:
        self._s.add(DeviceModel(
            id=device.id, user_id=device.user_id, installation_id=device.installation_id,
            public_key=device.public_key, name=device.name, platform=device.platform.value,
            created_at=device.created_at, last_seen_at=device.last_seen_at,
            has_pin_setup=device.has_pin_setup, auto_lock_minutes=device.auto_lock_minutes,
            biometric_enabled=device.biometric_enabled, city=device.city,
        ))
        await self._s.flush()

    async def update(self, device: Device) -> None:
        await self._s.execute(
            update(DeviceModel)
            .where(DeviceModel.id == device.id, DeviceModel.user_id == device.user_id)
            .values(public_key=device.public_key, name=device.name,
                    platform=device.platform.value, last_seen_at=device.last_seen_at,
                    has_pin_setup=device.has_pin_setup,
                    auto_lock_minutes=device.auto_lock_minutes,
                    biometric_enabled=device.biometric_enabled, city=device.city)
        )


class SqlSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get(self, session_id: UUID) -> Session | None:
        m = await self._s.get(SessionModel, session_id)
        return _session(m) if m else None

    async def add(self, session: Session) -> None:
        self._s.add(SessionModel(id=session.id, user_id=session.user_id,
                                 device_id=session.device_id, created_at=session.created_at))
        await self._s.flush()

    async def list_active_for_user(self, user_id: UUID) -> list[Session]:
        rows = await self._s.scalars(
            select(SessionModel).where(SessionModel.user_id == user_id,
                                       SessionModel.revoked_at.is_(None))
        )
        return [_session(m) for m in rows]

    async def _revoke(self, reason: RevokeReason, at: datetime, *where: object) -> int:
        result = await self._s.execute(
            update(SessionModel)
            .where(SessionModel.revoked_at.is_(None), *where)  # type: ignore[arg-type]
            .values(revoked_at=at, revoke_reason=reason.value)
        )
        return result.rowcount or 0  # type: ignore[attr-defined]

    async def revoke(self, session_id: UUID, reason: RevokeReason, at: datetime) -> None:
        await self._revoke(reason, at, SessionModel.id == session_id)

    async def revoke_for_device(self, user_id: UUID, device_id: UUID, reason: RevokeReason,
                                at: datetime) -> int:
        return await self._revoke(reason, at, SessionModel.user_id == user_id,
                                  SessionModel.device_id == device_id)

    async def revoke_all_for_user(self, user_id: UUID, reason: RevokeReason, at: datetime,
                                  *, except_device_id: UUID | None = None) -> int:
        where = [SessionModel.user_id == user_id]
        if except_device_id is not None:
            where.append(SessionModel.device_id != except_device_id)
        return await self._revoke(reason, at, *where)


class SqlRefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        m = await self._s.scalar(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        if m is None:
            return None
        return RefreshToken(id=m.id, session_id=m.session_id, token_hash=m.token_hash,
                            created_at=m.created_at, expires_at=m.expires_at, used_at=m.used_at)

    async def add(self, token: RefreshToken) -> None:
        self._s.add(RefreshTokenModel(id=token.id, session_id=token.session_id,
                                      token_hash=token.token_hash, created_at=token.created_at,
                                      expires_at=token.expires_at))
        await self._s.flush()

    async def mark_used(self, token_id: UUID, at: datetime) -> bool:
        result = await self._s.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id, RefreshTokenModel.used_at.is_(None))
            .values(used_at=at)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]
