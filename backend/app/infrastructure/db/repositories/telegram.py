from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.telegram.entities import TelegramLink
from app.infrastructure.db.models import TelegramLinkModel

M = TelegramLinkModel


class SqlTelegramLinkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get(self, phone_index: str) -> TelegramLink | None:
        m = await self._s.get(M, phone_index, populate_existing=True)
        if m is None:
            return None
        return TelegramLink(phone_index=m.phone_index, chat_id=m.chat_id,
                            telegram_user_id=m.telegram_user_id, language=m.language,
                            linked_at=m.linked_at)

    async def save(self, link: TelegramLink) -> None:
        await self._s.execute(delete(M).where(M.chat_id == link.chat_id,
                                              M.phone_index != link.phone_index))
        m = await self._s.scalar(select(M).where(M.phone_index == link.phone_index))
        if m is None:
            self._s.add(M(phone_index=link.phone_index, chat_id=link.chat_id,
                          telegram_user_id=link.telegram_user_id, language=link.language,
                          linked_at=link.linked_at))
        else:
            m.chat_id, m.telegram_user_id = link.chat_id, link.telegram_user_id
            m.language, m.linked_at = link.language, link.linked_at
        await self._s.flush()

    async def delete(self, phone_index: str) -> None:
        await self._s.execute(delete(M).where(M.phone_index == phone_index))

    async def delete_by_chat(self, chat_id: int) -> int:
        result = await self._s.execute(delete(M).where(M.chat_id == chat_id))
        return result.rowcount or 0  # type: ignore[attr-defined]
