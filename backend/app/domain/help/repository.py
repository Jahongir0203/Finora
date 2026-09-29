from typing import Protocol

from app.domain.help.entities import FaqItem


class FaqRepository(Protocol):
    async def for_language(self, language: str) -> list[FaqItem]: ...
    async def replace_language(self, language: str, items: list[FaqItem]) -> None: ...
