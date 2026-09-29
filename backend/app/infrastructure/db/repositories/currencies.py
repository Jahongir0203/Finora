from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.currencies.entities import CurrencyRate
from app.infrastructure.db.models import CurrencyRateModel


class SqlCurrencyRateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def all(self) -> dict[str, CurrencyRate]:
        rows = await self._s.scalars(select(CurrencyRateModel))
        return {m.code: CurrencyRate(code=m.code, rate_to_uzs=Decimal(str(m.rate_to_uzs)),
                                     rate_date=m.rate_date, updated_at=m.updated_at)
                for m in rows}

    async def save(self, rate: CurrencyRate) -> None:
        m = await self._s.get(CurrencyRateModel, rate.code)
        if m is None:
            self._s.add(CurrencyRateModel(code=rate.code, rate_to_uzs=rate.rate_to_uzs,
                                          rate_date=rate.rate_date, updated_at=rate.updated_at))
        else:
            m.rate_to_uzs, m.rate_date, m.updated_at = (rate.rate_to_uzs, rate.rate_date,
                                                        rate.updated_at)
        await self._s.flush()
