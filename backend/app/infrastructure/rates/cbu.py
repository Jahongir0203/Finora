"""O'zbekiston Markaziy banki kurslari (cbu.uz JSON). Kuniga bir marta (BE-1602).

Javob: [{"Ccy": "USD", "Rate": "12650.25", "Nominal": "1", ...}, ...] — Rate / Nominal.
"""

import logging
from decimal import Decimal, InvalidOperation

import httpx

from app.domain.currencies.entities import SUPPORTED_CURRENCIES

logger = logging.getLogger("finora.currencies")


class CbuRatesProvider:
    def __init__(self, url: str, client: httpx.AsyncClient | None = None) -> None:
        self._url = url
        self._client = client or httpx.AsyncClient(timeout=10.0)

    async def fetch(self) -> dict[str, Decimal]:
        r = await self._client.get(self._url)
        r.raise_for_status()
        out: dict[str, Decimal] = {}
        for item in r.json():
            code = str(item.get("Ccy", "")).upper()
            if code not in SUPPORTED_CURRENCIES:
                continue
            try:
                rate = Decimal(str(item["Rate"])) / Decimal(str(item.get("Nominal") or "1"))
            except (InvalidOperation, KeyError, ZeroDivisionError):
                continue
            if rate > 0:
                out[code] = rate.quantize(Decimal("0.0001"))
        return out

    async def aclose(self) -> None:
        await self._client.aclose()
