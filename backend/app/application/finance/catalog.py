"""Kategoriyalar katalogi: tizim (kodda) + user (bazada) + limit/nom override (prefs)."""

from uuid import UUID

from app.application.common.uow import UnitOfWork
from app.core.i18n import t
from app.domain.categories.entities import (
    SYSTEM_CATEGORIES,
    Category,
    CategoryType,
)
from app.domain.common.errors import ValidationFailedError
from app.domain.transactions.entities import TransactionType


class CategoryCatalog:
    def __init__(self, categories: dict[str, Category]) -> None:
        self._by_id = categories

    @classmethod
    async def load(cls, uow: UnitOfWork, user_id: UUID, locale: str | None = None,
                   *, include_deleted_ids: set[str] | None = None) -> "CategoryCatalog":
        prefs = await uow.categories.prefs(user_id)
        result: dict[str, Category] = {}
        for sc in SYSTEM_CATEGORIES.values():
            pref = prefs.get(sc.id)
            result[sc.id] = Category(
                id=sc.id,
                name=(pref.name_override if pref and pref.name_override
                      else t(f"category.{sc.id}", locale)),
                icon=sc.icon, color=sc.color, type=sc.type, is_system=True,
                monthly_limit=pref.monthly_limit if pref else None,
            )
        for uc in await uow.categories.list_for_user(user_id):
            pref = prefs.get(str(uc.id))
            result[str(uc.id)] = Category(
                id=str(uc.id), name=uc.name, icon=uc.icon, color=uc.color, type=uc.type,
                is_system=False, monthly_limit=pref.monthly_limit if pref else None,
            )
        return cls(result)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self._by_id.values())

    def get(self, category_id: str) -> Category | None:
        return self._by_id.get(category_id)

    def name(self, category_id: str) -> str:
        c = self._by_id.get(category_id)
        return c.name if c else category_id

    def require(self, category_id: str, tx_type: TransactionType | None = None) -> Category:
        """Kategoriya userga tegishli va (berilsa) tranzaksiya turiga mos bo'lishi shart."""
        category = self._by_id.get(category_id)
        if category is None:
            raise ValidationFailedError("Kategoriya topilmadi", fields=["category_id"])
        if tx_type is TransactionType.EXPENSE and category.type is not CategoryType.EXPENSE:
            raise ValidationFailedError(fields=["category_id"], code="category_type_mismatch")
        if tx_type is TransactionType.INCOME and category.type is not CategoryType.INCOME:
            raise ValidationFailedError(fields=["category_id"], code="category_type_mismatch")
        return category

    def ids_matching(self, q: str) -> list[str]:
        """Qidiruv: nomi `q`ni o'z ichiga olgan kategoriyalar (BE-503)."""
        needle = q.casefold()
        return [c.id for c in self._by_id.values() if needle in c.name.casefold()]
