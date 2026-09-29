"""Kategoriyalar (BE-1501) va byudjetlar (BE-1001).

Byudjet — kategoriyaning `monthly_limit`i. `spent` har doim joriy oy tranzaksiyalaridan
hisoblanadi (oy o'tganda 0 dan boshlanadi, limit saqlanadi).
"""

from dataclasses import dataclass
from datetime import date, datetime, tzinfo
from typing import Any
from uuid import UUID

from app.application.auth.dto import AuthContext
from app.application.common.idempotency import run_idempotent
from app.application.common.interfaces import Clock
from app.application.common.uow import UnitOfWork
from app.application.finance.catalog import CategoryCatalog
from app.application.finance.ledger import Ledger
from app.core.config import Settings
from app.domain.categories.entities import (
    SYSTEM_CATEGORIES,
    Category,
    CategoryPref,
    CategoryType,
    UserCategory,
    ensure_category_name,
)
from app.domain.common.errors import (
    CategoryInUseError,
    ConflictError,
    NotFoundError,
    ValidationFailedError,
)
from app.domain.common.ids import uuid7
from app.domain.common.time import add_months, local_midnight

_UNSET: Any = object()


def category_to_dict(c: Category, spent: int = 0, count: int = 0) -> dict[str, Any]:
    return {"id": c.id, "name": c.name, "icon": c.icon, "color": c.color,
            "type": c.type.value, "is_system": c.is_system, "monthly_limit": c.monthly_limit,
            "spent": spent, "transactions_count": count}


def _user_category_id(category_id: str) -> UUID | None:
    if category_id in SYSTEM_CATEGORIES:
        return None
    try:
        return UUID(category_id)
    except ValueError:
        raise NotFoundError() from None


@dataclass(frozen=True, slots=True)
class BudgetLine:
    category_id: str
    limit: int
    spent: int

    @property
    def pct(self) -> int:
        return self.spent * 100 // self.limit if self.limit else 0

    @property
    def status(self) -> str:
        ratio = self.spent / self.limit if self.limit else 0
        if ratio > 1:
            return "over"
        return "warning" if ratio >= 0.75 else "normal"

    def to_dict(self) -> dict[str, Any]:
        return {"category_id": self.category_id, "limit": self.limit, "spent": self.spent,
                "pct": self.pct, "status": self.status, "left": self.limit - self.spent}


class CategoryService:
    def __init__(self, uow: UnitOfWork, clock: Clock, settings: Settings,
                 ledger: Ledger) -> None:
        self._uow = uow
        self._clock = clock
        self._s = settings
        self._ledger = ledger

    async def budgets(self, ctx: AuthContext, month: date | None, tz: tzinfo,
                      now: datetime) -> list[dict[str, Any]]:
        async with self._uow as uow:
            catalog = await CategoryCatalog.load(uow, ctx.user_id)
            if month is None:
                spent = await self._ledger.month_spend_by_category(uow, ctx.user_id, now, tz)
            else:
                spent = await uow.ledger.spend_by_category(
                    ctx.user_id, local_midnight(month, tz),
                    local_midnight(add_months(month, 1), tz))
        return [BudgetLine(c.id, c.monthly_limit, spent.get(c.id, 0)).to_dict()
                for c in catalog if c.monthly_limit and c.type is CategoryType.EXPENSE]

    async def list(self, ctx: AuthContext, tz: tzinfo,
                   type_: CategoryType | None = None) -> list[dict[str, Any]]:
        async with self._uow as uow:
            catalog = await CategoryCatalog.load(uow, ctx.user_id)
            spent = await self._ledger.month_spend_by_category(uow, ctx.user_id,
                                                               self._clock.now(), tz)
            counts = await uow.transactions.counts_by_category(ctx.user_id)
        return [category_to_dict(c, spent.get(c.id, 0), counts.get(c.id, 0))
                for c in catalog if type_ is None or c.type is type_]

    async def create(self, ctx: AuthContext, name: str, icon: str, color: str,
                     type_: CategoryType, monthly_limit: int | None,
                     idempotency_key: str | None) -> dict[str, Any]:
        async with self._uow as uow:
            async def action() -> dict[str, Any]:
                now = self._clock.now()
                category = UserCategory(id=uuid7(), user_id=ctx.user_id, name=name, icon=icon,
                                        color=color, type=type_, created_at=now,
                                        updated_at=now)
                await uow.categories.add(category)
                if monthly_limit is not None:
                    await uow.categories.save_pref(CategoryPref(
                        user_id=ctx.user_id, category_id=str(category.id),
                        monthly_limit=monthly_limit, updated_at=now))
                catalog = await CategoryCatalog.load(uow, ctx.user_id)
                created = catalog.get(str(category.id))
                assert created is not None
                return category_to_dict(created)

            return await run_idempotent(
                uow, user_id=ctx.user_id, key=idempotency_key, operation="category.create",
                payload={"name": name, "icon": icon, "color": color, "type": type_.value,
                         "monthly_limit": monthly_limit},
                now=self._clock.now(), ttl_seconds=self._s.idempotency_ttl_seconds, action=action,
            )

    async def update(self, ctx: AuthContext, category_id: str, *, name: str | None = None,
                     icon: str | None = None, color: str | None = None,
                     monthly_limit: int | None = _UNSET) -> dict[str, Any]:
        """Tizim kategoriyasida faqat limit va nom override o'zgaradi."""
        user_cat_id = _user_category_id(category_id)
        async with self._uow as uow:
            now = self._clock.now()
            prefs = await uow.categories.prefs(ctx.user_id)
            pref = prefs.get(category_id) or CategoryPref(
                user_id=ctx.user_id, category_id=category_id, updated_at=now)
            if user_cat_id is None:
                if icon is not None or color is not None:
                    raise ValidationFailedError("Tizim kategoriyasining ikon/rangi o'zgarmaydi",
                                                fields=[f for f, v in (("icon", icon),
                                                                       ("color", color)) if v])
                if name is not None:
                    pref.name_override = ensure_category_name(name)
            else:
                category = await uow.categories.get_for_user(ctx.user_id, user_cat_id)
                if category is None:
                    raise NotFoundError()
                if name is not None:
                    if await uow.categories.name_taken(ctx.user_id, name, exclude_id=category.id):
                        raise ConflictError("Bunday nomli kategoriya bor")
                    category.name = name
                if icon is not None:
                    category.icon = icon
                if color is not None:
                    category.color = color
                category.updated_at = now
                category.validate()
                await uow.categories.update(category)
            if monthly_limit is not _UNSET:
                pref.monthly_limit = monthly_limit
            pref.updated_at = now
            pref.__post_init__()
            await uow.categories.save_pref(pref)
            catalog = await CategoryCatalog.load(uow, ctx.user_id)
            await uow.commit()
        updated = catalog.get(category_id)
        assert updated is not None
        return category_to_dict(updated)

    async def delete(self, ctx: AuthContext, category_id: str,
                     reassign_to: str | None) -> None:
        user_cat_id = _user_category_id(category_id)
        if user_cat_id is None:
            raise ValidationFailedError("Tizim kategoriyasini o'chirib bo'lmaydi",
                                        fields=["category_id"])
        async with self._uow as uow:
            category = await uow.categories.get_for_user(ctx.user_id, user_cat_id)
            if category is None:
                raise NotFoundError()
            now = self._clock.now()
            if await uow.transactions.count_for_category(ctx.user_id, category_id):
                if reassign_to is None:
                    raise CategoryInUseError()
                catalog = await CategoryCatalog.load(uow, ctx.user_id)
                target = catalog.get(reassign_to)
                if target is None or reassign_to == category_id or target.type != category.type:
                    raise ValidationFailedError(fields=["reassign_to"],
                                                code="category_type_mismatch")
                await uow.transactions.reassign_category(ctx.user_id, category_id,
                                                         reassign_to, now)
            await uow.categories.soft_delete(ctx.user_id, user_cat_id, now)
            await uow.commit()
        await self._ledger.invalidate(ctx.user_id)
