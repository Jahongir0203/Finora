from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.help.entities import FaqItem
from app.infrastructure.db.models import FaqItemModel


class SqlFaqRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def for_language(self, language: str) -> list[FaqItem]:
        rows = await self._s.scalars(
            select(FaqItemModel).where(FaqItemModel.language == language)
            .order_by(FaqItemModel.position)
        )
        return [FaqItem(id=m.id, language=m.language, question=m.question, answer=m.answer,
                        position=m.position) for m in rows]

    async def replace_language(self, language: str, items: list[FaqItem]) -> None:
        await self._s.execute(delete(FaqItemModel).where(FaqItemModel.language == language))
        for i in items:
            self._s.add(FaqItemModel(id=i.id, language=i.language, question=i.question,
                                     answer=i.answer, position=i.position))
        await self._s.flush()
