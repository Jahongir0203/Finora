"""Hodisaga bog'liq bildirishnomalar (BE-403): byudjet 75% / 100%, goal milestone.

Asosiy tranzaksiya commit bo'lgandan KEYIN chaqiriladi; xato so'rovni yiqitmaydi.
dedupe_key tufayli bir oyda bir marta (byudjet) va har chegara uchun bir marta (goal).
"""

import logging
from datetime import datetime, tzinfo
from uuid import UUID

from app.application.common.interfaces import Notifier
from app.application.common.uow import UnitOfWork
from app.application.finance.catalog import CategoryCatalog
from app.application.finance.ledger import Ledger
from app.core.i18n import format_amount, t
from app.domain.common.time import month_key
from app.domain.goals.entities import crossed_milestones
from app.domain.notifications.entities import NotificationType

logger = logging.getLogger("finora.notifications")

BUDGET_WARNING_PCT = 75


async def check_budget(uow: UnitOfWork, ledger: Ledger, notifier: Notifier, user_id: UUID,
                       category_id: str, now: datetime, tz: tzinfo) -> None:
    try:
        catalog = await CategoryCatalog.load(uow, user_id)
        category = catalog.get(category_id)
        if category is None or not category.monthly_limit:
            return
        limit = category.monthly_limit
        spent = (await ledger.month_spend_by_category(uow, user_id, now, tz)).get(category_id, 0)
        pct = spent * 100 // limit
        month = month_key(now.astimezone(tz).date())
        if pct >= 100:
            level, title_key = 100, "notif.budget_exceeded.title"
        elif pct >= BUDGET_WARNING_PCT:
            level, title_key = BUDGET_WARNING_PCT, "notif.budget_warning.title"
        else:
            return

        def render(loc: str) -> tuple[str, str]:
            name = catalog.name(category_id) if category.is_system is False else t(
                f"category.{category_id}", loc)
            return (t(title_key, loc, category=name),
                    t("notif.budget.body", loc, spent=format_amount(spent),
                      limit=format_amount(limit)))

        await notifier.notify(user_id, NotificationType.BUDGET_EXCEEDED, render,
                              dedupe_key=f"budget:{category_id}:{month}:{level}")
    except Exception:
        logger.exception("budget_check_failed")


async def goal_milestones(notifier: Notifier, user_id: UUID, goal_id: UUID, goal_name: str,
                          before: int, after: int, target: int) -> None:
    for pct in crossed_milestones(before, after, target):
        body_key = "notif.goal_completed.body" if pct == 100 else "notif.goal_milestone.body"

        def render(loc: str, p: int = pct, k: str = body_key) -> tuple[str, str]:
            return t("notif.goal_milestone.title", loc, goal=goal_name, pct=p), t(k, loc)

        try:
            await notifier.notify(user_id, NotificationType.GOAL_MILESTONE, render,
                                  dedupe_key=f"goal:{goal_id}:{pct}")
        except Exception:
            logger.exception("goal_milestone_failed")
