"""Profil, sozlamalar, onboarding holati (BE-1301, 1302, 1802, 201, 205, 1303)."""

from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.audit import record_audit
from app.application.common.interfaces import Clock, Notifier, PhoneCipher
from app.application.common.uow import UnitOfWork
from app.core.i18n import SUPPORTED_LANGUAGES
from app.domain.audit.entities import AuditAction
from app.domain.auth.entities import AUTO_LOCK_CHOICES, Device, RevokeReason
from app.domain.common.errors import NotFoundError, ValidationFailedError
from app.domain.common.time import parse_tz
from app.domain.common.values import ensure_name
from app.domain.currencies.entities import SUPPORTED_CURRENCIES
from app.domain.users.entities import Theme, User

USER_SETTINGS = {"language", "currency", "theme", "notifications_enabled", "timezone"}
DEVICE_SETTINGS = {"auto_lock_minutes", "biometric_enabled"}


async def onboarding_state(uow: UnitOfWork, user: User) -> dict[str, bool]:
    return {
        "balance_set": user.balance_set,
        "has_transactions": await uow.transactions.has_any(user.id),
        "has_goals": bool(await uow.goals.list_for_user(user.id)),
        "has_reminders": bool(await uow.reminders.list_for_user(user.id)),
    }


def device_settings(d: Device) -> dict[str, Any]:
    return {"auto_lock_minutes": d.auto_lock_minutes, "biometric_enabled": d.biometric_enabled,
            "has_pin_setup": d.has_pin_setup}


class ProfileService:
    def __init__(self, uow: UnitOfWork, clock: Clock, cipher: PhoneCipher) -> None:
        self._uow = uow
        self._clock = clock
        self._cipher = cipher

    async def _user(self, uow: UnitOfWork, ctx: AuthContext) -> User:
        user = await uow.users.get(ctx.user_id)
        if user is None:
            raise NotFoundError()
        return user

    def _to_dict(self, user: User, device: Device | None, onboarding: dict[str, bool],
                 counts: dict[str, int]) -> dict[str, Any]:
        return {
            "id": str(user.id), "first_name": user.first_name, "last_name": user.last_name,
            "initials": user.initials,
            "phone_masked": self._cipher.decrypt(user.phone_ciphertext).masked(),
            "language": user.language, "currency": user.currency, "theme": user.theme.value,
            "notifications_enabled": user.notifications_enabled, "timezone": user.timezone,
            "device": device_settings(device) if device else None,
            "counts": counts, "onboarding": onboarding,
        }

    async def me(self, ctx: AuthContext, tz_header: str | None = None) -> dict[str, Any]:
        async with self._uow as uow:
            user = await self._user(uow, ctx)
            # Fon vazifalari (10:00, 09:00) to'g'ri vaqtda ishlashi uchun zonani eslab qolamiz
            if tz_header and parse_tz(tz_header) and tz_header != user.timezone:
                user.timezone = tz_header
                await uow.users.update(user)
                await uow.commit()
            device = await uow.devices.get_for_user(ctx.user_id, ctx.device_id)
            reminders = await uow.reminders.list_for_user(ctx.user_id)
            counts = {
                "accounts": len(await uow.accounts.list_for_user(ctx.user_id)),
                "categories": 10 + len(await uow.categories.list_for_user(ctx.user_id)),
                "reminders_enabled": sum(1 for r in reminders if r.enabled),
            }
            onboarding = await onboarding_state(uow, user)
        return self._to_dict(user, device, onboarding, counts)

    async def update_name(self, ctx: AuthContext, fields: dict[str, Any]) -> dict[str, Any]:
        async with self._uow as uow:
            user = await self._user(uow, ctx)
            for key in ("first_name", "last_name"):
                if key in fields:
                    value = fields[key]
                    setattr(user, key, ensure_name(value) if value else None)
            await uow.users.update(user)
            await uow.commit()
        return await self.me(ctx)

    async def update_settings(self, ctx: AuthContext, fields: dict[str, Any]) -> dict[str, Any]:
        """Foydalanuvchi darajasida: til, valyuta, mavzu, bildirishnomalar, vaqt zonasi.
        Qurilma darajasida: auto_lock_minutes, biometric_enabled (BE-205)."""
        if "language" in fields and fields["language"] not in SUPPORTED_LANGUAGES:
            raise ValidationFailedError("Til qo'llab-quvvatlanmaydi", fields=["language"])
        if "currency" in fields and fields["currency"] not in SUPPORTED_CURRENCIES:
            raise ValidationFailedError("Valyuta qo'llab-quvvatlanmaydi", fields=["currency"])
        if "timezone" in fields and parse_tz(fields["timezone"]) is None:
            raise ValidationFailedError("Vaqt zonasi noto'g'ri", fields=["timezone"])
        if "auto_lock_minutes" in fields and fields["auto_lock_minutes"] not in AUTO_LOCK_CHOICES:
            raise ValidationFailedError("auto_lock_minutes: 1, 3 yoki 5",
                                        fields=["auto_lock_minutes"])
        async with self._uow as uow:
            user = await self._user(uow, ctx)
            for key in USER_SETTINGS & fields.keys():
                value = Theme(fields[key]) if key == "theme" else fields[key]
                setattr(user, key, value)
            await uow.users.update(user)
            if DEVICE_SETTINGS & fields.keys():
                device = await uow.devices.get_for_user(ctx.user_id, ctx.device_id)
                if device is None:
                    raise NotFoundError()
                for key in DEVICE_SETTINGS & fields.keys():
                    setattr(device, key, fields[key])
                await uow.devices.update(device)
            await uow.commit()
        return await self.me(ctx)

    async def pin_setup(self, ctx: AuthContext, installation_id: UUID | None) -> dict[str, Any]:
        """BE-201: PIN o'rnatildi (qurilma darajasida). PIN'ning o'zi serverga kelmaydi."""
        async with self._uow as uow:
            device = await uow.devices.get_for_user(ctx.user_id, ctx.device_id)
            if device is None or (installation_id is not None
                                  and device.installation_id != installation_id):
                raise NotFoundError()
            device.has_pin_setup = True
            await uow.devices.update(device)
            await uow.commit()
        return device_settings(device)


class DeviceService:
    def __init__(self, uow: UnitOfWork, clock: Clock, notifier: Notifier) -> None:
        self._uow = uow
        self._clock = clock
        self._notifier = notifier

    async def list(self, ctx: AuthContext) -> list[dict[str, Any]]:
        async with self._uow as uow:
            active = {s.device_id for s in await uow.sessions.list_active_for_user(ctx.user_id)}
            devices = await uow.devices.list_for_user(ctx.user_id)
        return [{"id": str(d.id), "name": d.name, "platform": d.platform.value, "city": d.city,
                 "last_active_at": d.last_seen_at.isoformat(),
                 "created_at": d.created_at.isoformat(), "current": d.id == ctx.device_id}
                for d in devices if d.id in active]

    async def logout_others(self, ctx: AuthContext) -> int:
        """BE-1303: joriydan tashqari barcha qurilmalar + `security` bildirishnoma."""
        async with self._uow as uow:
            n = await uow.sessions.revoke_all_for_user(
                ctx.user_id, RevokeReason.LOGOUT_ALL, self._clock.now(),
                except_device_id=ctx.device_id)
            await record_audit(uow, self._clock, AuditAction.LOGOUT_ALL, user_id=ctx.user_id,
                               device_id=ctx.device_id, revoked=n)
            await uow.commit()
        await self._notifier.security(ctx.user_id, "notif.security.logout_all")
        return n
