"""Fiskal QR (ofd.soliq.uz) parser va do'kon nomidan kategoriya taxmini (BE-701, BE-702)."""

import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

from app.domain.receipts.entities import ReceiptItem

_FISCAL_HOSTS = ("ofd.soliq.uz", "soliq.uz")
_TS_FORMATS = ("%Y%m%d%H%M%S", "%Y%m%d%H%M", "%Y-%m-%dT%H:%M:%S")
_TASHKENT = ZoneInfo("Asia/Tashkent")


@dataclass(frozen=True, slots=True)
class FiscalQr:
    terminal_id: str  # t — fiskal modul (FM) raqami
    receipt_number: str  # r — chek raqami
    issued_at: datetime  # c — sana/vaqt (mahalliy)
    fiscal_sign: str  # s — fiskal belgi


def parse_fiscal_qr(payload: str) -> FiscalQr | None:
    """Soliq qo'mitasi fiskal chek QR'i: https://ofd.soliq.uz/check?t=..&r=..&c=..&s=..
    Boshqa QR (havola, matn) — None."""
    payload = payload.strip()
    if len(payload) > 512:
        return None
    try:
        parts = urlsplit(payload)
    except ValueError:
        return None
    host = (parts.hostname or "").lower()
    if parts.scheme not in ("http", "https") or not any(
            host == h or host.endswith("." + h) for h in _FISCAL_HOSTS):
        return None
    q = {k: v[0].strip() for k, v in parse_qs(parts.query).items() if v}
    t, r, c, s = (q.get(k, "") for k in ("t", "r", "c", "s"))
    if not (re.fullmatch(r"[A-Za-z0-9]{6,32}", t) and re.fullmatch(r"\d{1,20}", r)
            and re.fullmatch(r"\d{6,20}", s)):
        return None
    for fmt in _TS_FORMATS:
        try:
            issued = datetime.strptime(c, fmt).replace(tzinfo=_TASHKENT)
            break
        except ValueError:
            continue
    else:
        return None
    return FiscalQr(terminal_id=t, receipt_number=r, issued_at=issued, fiscal_sign=s)


# Do'kon/brend nomi -> tizim kategoriyasi
_MERCHANT_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("groceries", ("korzinka", "makro", "havas", "baraka", "carrefour", "supermarket",
                   "market", "oziq", "продукт", "магазин", "anglesey", "globus")),
    ("food", ("evos", "kfc", "oqtepa", "lavash", "bellissimo", "max way", "maxway", "cafe",
              "kafe", "restaurant", "restoran", "coffee", "kofe", "burger", "pizza", "bon!",
              "safia", "chaixona", "choyxona")),
    ("transport", ("yandex go", "yandex.go", "mytaxi", "uklon", "taxi", "taksi", "metro",
                   "benzin", "petrol", "azs", "uzbekneftegaz", "lukoil", "ngz")),
    ("health", ("apteka", "dorixona", "pharm", "аптека", "clinic", "klinika", "med")),
    ("bills", ("uzbektelecom", "beeline", "ucell", "mobiuz", "uzmobile", "hududgaz",
               "elektr", "energo", "suv", "issiqlik")),
    ("subs", ("netflix", "spotify", "youtube", "apple.com", "google", "itunes", "kinopoisk",
              "telegram premium")),
    ("shopping", ("texnomart", "mediapark", "zara", "lc waikiki", "uzum", "wildberries",
                  "ozon", "idea", "artel")),
]


def suggest_category(merchant: str | None, items: list[ReceiptItem] | None = None) -> str | None:
    text = " ".join([merchant or "", *(i.name for i in items or [])]).casefold()
    if not text.strip():
        return None
    for category, words in _MERCHANT_RULES:
        if any(w in text for w in words):
            return category
    return None
