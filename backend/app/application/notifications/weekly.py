"""Haftalik hisobot (BE-403): har dushanba 09:00 (user vaqtida), oldingi hafta ma'lumoti bo'lsa."""

from collections.abc import AsyncIterator, Callable
from datetime import time, timedelta

from app.application.common.interfaces import Clock, Notifier
from app.application.common.uow import UnitOfWork
from app.core.i18n import format_amount, t
from app.domain.common.time import local_midnight, tz_or_default, week_start
from app.domain.notifications.entities import NotificationType
from app.domain.users.entities import User

WEEKLY_LOCAL_TIME = time(9, 0)
_PAGE = 500


async def iter_users(uow_factory: Callable[[], UnitOfWork]) -> AsyncIterator[User]:
    after = None
    while True:
        async with uow_factory() as uow:
            users = await uow.users.list_ids(after=after, limit=_PAGE)
        if not users:
            return
        for u in users:
            yield u
        after = users[-1].id


class WeeklyReportJob:
    def __init__(self, uow_factory: Callable[[], UnitOfWork], clock: Clock,
                 notifier: Notifier) -> None:
        self._uow = uow_factory
        self._clock = clock
        self._notifier = notifier

    async def run(self) -> int:
        sent = 0
        now = self._clock.now()
        async for user in iter_users(self._uow):
            tz = tz_or_default(user.timezone)
            local = now.astimezone(tz)
            if local.weekday() != 0 or local.time() < WEEKLY_LOCAL_TIME:
                continue
            this_week = week_start(local.date())
            last, prev = this_week - timedelta(days=7), this_week - timedelta(days=14)
            async with self._uow() as uow:
                _, spent = await uow.ledger.totals(user.id, local_midnight(last, tz),
                                                   local_midnight(this_week, tz))
                _, before = await uow.ledger.totals(user.id, local_midnight(prev, tz),
                                                    local_midnight(last, tz))
            if spent == 0:
                continue
            if before:
                pct = round((spent - before) * 100 / before)
                key = ("notif.weekly_report.up" if pct > 0 else
                       "notif.weekly_report.down" if pct < 0 else "notif.weekly_report.same")
            else:
                pct, key = 0, "notif.weekly_report.same"
            iso = last.isocalendar()

            def render(loc: str, key: str = key, pct: int = pct,
                       spent: int = spent) -> tuple[str, str]:
                return (t("notif.weekly_report.title", loc),
                        t(key, loc, pct=abs(pct), amount=format_amount(spent)))

            if await self._notifier.notify(user.id, NotificationType.WEEKLY_REPORT, render,
                                           dedupe_key=f"weekly:{iso.year}-W{iso.week:02d}"):
                sent += 1
        return sent
