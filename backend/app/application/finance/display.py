"""Ko'rsatish valyutasi (BE-1602): summalar bazada UZS'da, javobda `*_display` ham beriladi."""

from dataclasses import dataclass
from decimal import Decimal

from app.application.common.uow import UnitOfWork
from app.domain.currencies.entities import convert_from_uzs
from app.domain.users.entities import BASE_CURRENCY


@dataclass(frozen=True, slots=True)
class DisplayCurrency:
    currency: str
    rate: Decimal | None  # None — UZS yoki kurs hali olinmagan

    def amount(self, value: int | None) -> str | None:
        if value is None or self.rate is None:
            return None
        return convert_from_uzs(value, self.rate)

    @property
    def active(self) -> bool:
        return self.rate is not None


async def display_currency(uow: UnitOfWork, currency: str) -> DisplayCurrency:
    if currency == BASE_CURRENCY:
        return DisplayCurrency(BASE_CURRENCY, None)
    rate = (await uow.currency_rates.all()).get(currency)
    return DisplayCurrency(currency, rate.rate_to_uzs if rate and rate.rate_to_uzs > 0 else None)
