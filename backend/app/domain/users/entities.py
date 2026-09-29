from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.core.i18n import DEFAULT_LANGUAGE
from app.domain.common.time import DEFAULT_TZ_NAME

BASE_CURRENCY = "UZS"


class Theme(StrEnum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


@dataclass(slots=True)
class User:
    id: UUID
    # Telefon field-level shifrlangan (AES-GCM); qidiruv faqat HMAC blind-index orqali
    phone_ciphertext: bytes
    phone_index: str
    created_at: datetime
    first_name: str | None = None
    last_name: str | None = None
    language: str = DEFAULT_LANGUAGE
    # Ko'rsatish valyutasi. Summalar bazada har doim UZS'da (BE-1602)
    currency: str = BASE_CURRENCY
    theme: Theme = Theme.SYSTEM
    notifications_enabled: bool = True
    # Fon vazifalari (eslatma 10:00, haftalik hisobot 09:00) mahalliy vaqtda ishlashi uchun
    timezone: str = DEFAULT_TZ_NAME
    # Onboarding: boshlang'ich balans kiritilganmi ("Skip" -> False qoladi)
    balance_set: bool = False

    @property
    def initials(self) -> str:
        parts = [p for p in (self.first_name, self.last_name) if p]
        return "".join(p[0].upper() for p in parts)[:2]
