"""Offline sync (BE-302): `GET /v1/sync?since=` — o'zgargan va o'chirilgan yozuvlar delta'si.

Offline yaratilgan yozuvlar oddiy POST'lar bilan (`Idempotency-Key` + `client_created_at`)
yuboriladi, shuning uchun takroriy sync dublikat yaratmaydi.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from app.application.accounts.use_cases import account_to_dict
from app.application.categories.use_cases import category_to_dict
from app.application.common.uow import UnitOfWork
from app.application.finance.catalog import CategoryCatalog
from app.application.finance.ledger import Ledger
from app.application.goals.use_cases import GoalView
from app.application.reminders.use_cases import reminder_to_dict
from app.application.transactions.use_cases import transaction_to_dict
from app.domain.categories.entities import Category

MAX_PER_ENTITY = 500


def _split(rows: list[Any], render: Any) -> dict[str, Any]:
    deleted_attr = "deleted_at"
    changed, deleted = [], []
    for r in rows:
        gone = getattr(r, deleted_attr, None) or getattr(r, "archived_at", None)
        if gone is not None:
            deleted.append(str(r.id))
        else:
            changed.append(render(r))
    return {"changed": changed, "deleted": deleted}


class SyncService:
    def __init__(self, uow: UnitOfWork, ledger: Ledger) -> None:
        self._uow = uow
        self._ledger = ledger

    async def execute(self, user_id: UUID, since: datetime, now: datetime) -> dict[str, Any]:
        lim = MAX_PER_ENTITY
        async with self._uow as uow:
            txs = await uow.transactions.changed_since(user_id, since, lim + 1)
            goals = await uow.goals.changed_since(user_id, since, lim + 1)
            reminders = await uow.reminders.changed_since(user_id, since, lim + 1)
            cats = await uow.categories.changed_since(user_id, since, lim + 1)
            accounts = await uow.accounts.changed_since(user_id, since, lim + 1)
            saved = await uow.goals.saved_amounts(user_id)
            balances = await self._ledger.account_balances(
                uow, user_id, [a for a in accounts if a.archived_at is None])
            catalog = await CategoryCatalog.load(uow, user_id)
        has_more = any(len(x) > lim for x in (txs, goals, reminders, cats, accounts))
        today = now.date()

        def render_cat(c: Any) -> dict[str, Any]:
            view: Category | None = catalog.get(str(c.id))
            return category_to_dict(view) if view else {"id": str(c.id)}

        return {
            "server_time": now.isoformat(),
            "has_more": has_more,
            "transactions": _split(txs[:lim], transaction_to_dict),
            "goals": _split(goals[:lim], lambda g: GoalView(g, saved.get(g.id, 0),
                                                            today).to_dict()),
            "reminders": _split(reminders[:lim], lambda r: reminder_to_dict(r, today)),
            "categories": _split(cats[:lim], render_cat),
            "accounts": _split(accounts[:lim],
                               lambda a: account_to_dict(a, balances.get(a.id, 0))),
        }
