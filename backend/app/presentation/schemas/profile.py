from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, StringConstraints

from app.domain.users.entities import Theme
from app.presentation.schemas.auth import OnboardingOut
from app.presentation.schemas.common import StrictModel

PersonName = Annotated[str, StringConstraints(max_length=64)]


class ProfileUpdateIn(StrictModel):
    first_name: PersonName | None = None
    last_name: PersonName | None = None


class SettingsIn(StrictModel):
    """Foydalanuvchi: language, currency, theme, notifications_enabled, timezone.
    Qurilma: auto_lock_minutes, biometric_enabled (BE-205)."""

    language: str | None = None
    currency: str | None = None
    theme: Theme | None = None
    notifications_enabled: bool | None = None
    timezone: str | None = None
    auto_lock_minutes: Literal[1, 3, 5] | None = None
    biometric_enabled: bool | None = None


class PinSetupIn(StrictModel):
    device_id: UUID | None = None


class DeviceSettingsOut(BaseModel):
    auto_lock_minutes: int
    biometric_enabled: bool
    has_pin_setup: bool


class CountsOut(BaseModel):
    accounts: int
    categories: int
    reminders_enabled: int


class MeOut(BaseModel):
    id: UUID
    first_name: str | None
    last_name: str | None
    initials: str
    phone_masked: str
    language: str
    currency: str
    theme: Theme
    notifications_enabled: bool
    timezone: str
    device: DeviceSettingsOut | None
    counts: CountsOut
    onboarding: OnboardingOut


class DeleteAccountIn(StrictModel):
    code: Annotated[str, StringConstraints(pattern=r"^\d{6}$")]
