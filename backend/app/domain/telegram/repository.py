from typing import Protocol

from app.domain.telegram.entities import TelegramLink


class TelegramLinkRepository(Protocol):
    async def get(self, phone_index: str) -> TelegramLink | None: ...
    async def save(self, link: TelegramLink) -> None:
        """Upsert. Shu chat boshqa raqamga ulangan bo'lsa (raqam almashgan) — eski bog'lanish
        o'chiriladi: bitta Telegram akkaunt — bitta raqam."""
        ...
    async def delete_by_chat(self, chat_id: int) -> int: ...
    async def delete(self, phone_index: str) -> None:
        """Akkaunt o'chirilganda — bog'lanish ham shaxsiy ma'lumot."""
        ...
