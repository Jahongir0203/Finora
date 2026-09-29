from fastapi import APIRouter

from app.presentation.api.v1 import (
    accounts,
    ai,
    auth,
    categories,
    currencies,
    devices,
    exports,
    goals,
    help,
    home,
    insights,
    me,
    notifications,
    onboarding,
    receipts,
    reminders,
    stats,
    sync,
    transactions,
)

api_router = APIRouter(prefix="/v1")
for module in (auth, me, devices, notifications, home, onboarding, accounts, categories,
               transactions, goals, reminders, exports, receipts, stats, insights, ai, sync,
               currencies, help):
    api_router.include_router(module.router)
api_router.include_router(accounts.transfers_router)
api_router.include_router(categories.budgets_router)
