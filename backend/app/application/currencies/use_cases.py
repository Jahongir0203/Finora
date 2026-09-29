"""Valyuta kurslari (BE-1602). Manba — CBU (cbu.uz), kuniga bir marta yangilanadi."""

import logging
from decimal import Decimal
from typing import Any

from app.application.common.interfaces import Clock, RatesProvider
from app.application.common.uow import UnitOfWork
from app.domain.currencies.entities import SUPPORTED_CURRENCIES, CurrencyRate

logger = logging.getLogger("finora.currencies")


class CurrencyService:
    def __init__(self, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    async def list(self) -> list[dict[str, Any]]:
        async with self._uow as uow:
            rates = await uow.currency_rates.all()
        out = []
        for c in SUPPORTED_CURRENCIES.values():
            rate = Decimal(1) if c.code == "UZS" else (rates[c.code].rate_to_uzs
                                                         if c.code in rates else None)
            out.append({"code": c.code, "symbol": c.symbol, "name": c.name,
                        "rate_to_uzs": str(rate) if rate is not None else None,
                        "rate_date": (rates[c.code].rate_date.isoformat()
                                      if c.code in rates else None)})
        return out


class RatesJob:
    def __init__(self, uow: UnitOfWork, provider: RatesProvider, clock: Clock) -> None:
        self._uow = uow
        self._provider = provider
        self._clock = clock

    async def run(self) -> int:
        try:
            fetched = await self._provider.fetch()
        except Exception:
            logger.exception("rates_fetch_failed")
            return 0
        now = self._clock.now()
        saved = 0
        async with self._uow as uow:
            for code, rate in fetched.items():
                if code in SUPPORTED_CURRENCIES and code != "UZS" and rate > 0:
                    await uow.currency_rates.save(CurrencyRate(code=code, rate_to_uzs=rate,
                                                               rate_date=now.date(),
                                                               updated_at=now))
                    saved += 1
            await uow.commit()
        return saved
