from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.categories.entities import CategoryPref, CategoryType, UserCategory
from app.domain.common.errors import ConflictError
from app.infrastructure.db.models import CategoryModel, CategoryPrefModel


def _category(m: CategoryModel) -> UserCategory:
    return UserCategory(id=m.id, user_id=m.user_id, name=m.name, icon=m.icon, color=m.color,
                        type=CategoryType(m.type), created_at=m.created_at,
                        updated_at=m.updated_at, deleted_at=m.deleted_at)


def name_key(name: str) -> str:
    return name.strip().casefold()


class SqlCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def name_taken(self, user_id: UUID, name: str,
                         exclude_id: UUID | None = None) -> bool:
        stmt = select(CategoryModel.id).where(
            CategoryModel.user_id == user_id, CategoryModel.name_key == name_key(name),
            CategoryModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            stmt = stmt.where(CategoryModel.id != exclude_id)
        return await self._s.scalar(stmt.limit(1)) is not None

    async def add(self, category: UserCategory) -> None:
        if await self.name_taken(category.user_id, category.name):
            raise ConflictError("Bunday nomli kategoriya bor")
        self._s.add(CategoryModel(
            id=category.id, user_id=category.user_id, name=category.name,
            name_key=name_key(category.name), icon=category.icon, color=category.color,
            type=category.type.value, created_at=category.created_at,
            updated_at=category.updated_at,
        ))
        await self._s.flush()

    async def get_for_user(self, user_id: UUID, category_id: UUID) -> UserCategory | None:
        m = await self._s.scalar(
            select(CategoryModel).where(CategoryModel.id == category_id,
                                        CategoryModel.user_id == user_id,
                                        CategoryModel.deleted_at.is_(None))
        )
        return _category(m) if m else None

    async def list_for_user(self, user_id: UUID) -> list[UserCategory]:
        rows = await self._s.scalars(
            select(CategoryModel).where(CategoryModel.user_id == user_id,
                                        CategoryModel.deleted_at.is_(None))
            .order_by(CategoryModel.id)
        )
        return [_category(m) for m in rows]

    async def update(self, category: UserCategory) -> None:
        await self._s.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category.id, CategoryModel.user_id == category.user_id)
            .values(name=category.name, name_key=name_key(category.name), icon=category.icon,
                    color=category.color, updated_at=category.updated_at)
        )

    async def soft_delete(self, user_id: UUID, category_id: UUID, at: datetime) -> bool:
        result = await self._s.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category_id, CategoryModel.user_id == user_id,
                   CategoryModel.deleted_at.is_(None))
            .values(deleted_at=at, updated_at=at)
        )
        return bool(result.rowcount)  # type: ignore[attr-defined]

    async def prefs(self, user_id: UUID) -> dict[str, CategoryPref]:
        rows = await self._s.scalars(
            select(CategoryPrefModel).where(CategoryPrefModel.user_id == user_id)
        )
        return {m.category_id: CategoryPref(user_id=m.user_id, category_id=m.category_id,
                                            monthly_limit=m.monthly_limit,
                                            name_override=m.name_override,
                                            updated_at=m.updated_at) for m in rows}

    async def save_pref(self, pref: CategoryPref) -> None:
        m = await self._s.get(CategoryPrefModel, (pref.user_id, pref.category_id))
        if m is None:
            self._s.add(CategoryPrefModel(
                user_id=pref.user_id, category_id=pref.category_id,
                monthly_limit=pref.monthly_limit, name_override=pref.name_override,
                updated_at=pref.updated_at,
            ))
        else:
            m.monthly_limit = pref.monthly_limit
            m.name_override = pref.name_override
            m.updated_at = pref.updated_at
        await self._s.flush()

    async def changed_since(self, user_id: UUID, since: datetime,
                            limit: int) -> list[UserCategory]:
        rows = await self._s.scalars(
            select(CategoryModel).where(CategoryModel.user_id == user_id,
                                        CategoryModel.updated_at > since)
            .order_by(CategoryModel.updated_at).limit(limit)
        )
        return [_category(m) for m in rows]
