"""Strukturalangan (JSON) loglash.

02-backend.md, 9-bo'lim: loglarda token, OTP, to'liq telefon raqami, summalar va
chek matni bo'lmaydi. Filtr har bir yozuvni chiqishdan oldin tozalaydi.
"""

import json
import logging
import re
from contextvars import ContextVar
from typing import Any

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)

_PHONE_RE = re.compile(r"\+?998[\s-]?(\d{2})[\s-]?\d{3}[\s-]?\d{2}[\s-]?(\d{2})")
_JWT_RE = re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]+")
_SENSITIVE_KEYS = {
    "token",
    "access_token",
    "refresh_token",
    "otp",
    "code",
    "authorization",
    "phone",
    "amount",
    "pin",
    "signature",
    "receipt_text",
    "public_key",
    "question",
    "answer",
}


def mask_phone(phone: str) -> str:
    """+998901234567 -> +998 90 *** ** 67"""
    digits = re.sub(r"\D", "", phone)
    if len(digits) != 12:
        return "***"
    return f"+{digits[:3]} {digits[3:5]} *** ** {digits[-2:]}"


def scrub_text(text: str) -> str:
    text = _PHONE_RE.sub(lambda m: f"+998 {m.group(1)} *** ** {m.group(2)}", text)
    return _JWT_RE.sub("[jwt]", text)


def scrub(value: Any, key: str | None = None) -> Any:
    if key is not None and key.lower() in _SENSITIVE_KEYS:
        return "[redacted]"
    if isinstance(value, dict):
        return {k: scrub(v, str(k)) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [scrub(v) for v in value]
    if isinstance(value, str):
        return scrub_text(value)
    return value


_STD_ATTRS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": scrub_text(record.getMessage()),
            "request_id": request_id_ctx.get(),
        }
        extra = {k: v for k, v in record.__dict__.items() if k not in _STD_ATTRS}
        if extra:
            payload["extra"] = scrub(extra)
        if record.exc_info:
            # Stack trace faqat logga (mijozga emas), matni ham tozalanadi
            payload["exc"] = scrub_text(self.formatException(record.exc_info))
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    # uvicorn access log so'rov query-stringini yozadi — o'chiramiz, o'zimizniki bor
    logging.getLogger("uvicorn.access").disabled = True
