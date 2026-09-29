"""Valyutalar (BE-1602). Summalar bazada UZS'da; boshqa valyuta faqat ko'rsatish uchun."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True, slots=True)
class CurrencyInfo:
    code: str
    symbol: str
    name: str


SUPPORTED_CURRENCIES: dict[str, CurrencyInfo] = {c.code: c for c in (
    CurrencyInfo("UZS", "so'm", "Uzbek so'm"),
    CurrencyInfo("USD", "$", "US dollar"),
    CurrencyInfo("EUR", "€", "Euro"),
    CurrencyInfo("RUB", "₽", "Russian ruble"),
    CurrencyInfo("KZT", "₸", "Kazakhstani tenge"),
    CurrencyInfo("GBP", "£", "British pound"),
    CurrencyInfo("CNY", "¥", "Chinese yuan"),
    CurrencyInfo("TRY", "₺", "Turkish lira"),
)}


@dataclass(slots=True)
class CurrencyRate:
    code: str
    # 1 birlik valyuta necha so'm (CBU kursi), masalan Decimal("12650.25")
    rate_to_uzs: Decimal
    rate_date: date
    updated_at: datetime


def convert_from_uzs(amount: int, rate: Decimal) -> str:
    """So'mdagi summani ko'rsatish valyutasiga: "1970.25" (satr — float xatosiz)."""
    value = (Decimal(amount) / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{value:.2f}"
