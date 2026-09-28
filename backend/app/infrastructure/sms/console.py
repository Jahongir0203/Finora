import sys

from app.core.config import Environment, Settings
from app.domain.common.values import PhoneNumber


class ConsoleSmsSender:
    """Faqat dev: SMS matnini stderr'ga chiqaradi (log tizimiga emas). Prod'da ishga tushmaydi."""

    def __init__(self, settings: Settings) -> None:
        if settings.env is Environment.PROD:
            raise RuntimeError("ConsoleSmsSender prod'da taqiqlangan")

    async def send(self, phone: PhoneNumber, text: str) -> None:
        print(f"[DEV SMS → {phone.masked()}] {text}", file=sys.stderr)  # noqa: T201


class InMemorySmsSender:
    """Testlar uchun: yuborilgan xabarlarni yig'adi."""

    def __init__(self) -> None:
        self.outbox: list[tuple[str, str]] = []

    async def send(self, phone: PhoneNumber, text: str) -> None:
        self.outbox.append((phone.value, text))
