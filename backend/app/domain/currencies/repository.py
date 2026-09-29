from typing import Protocol

from app.domain.currencies.entities import CurrencyRate


class CurrencyRateRepository(Protocol):
    async def all(self) -> dict[str, CurrencyRate]: ...
    async def save(self, rate: CurrencyRate) -> None: ...
