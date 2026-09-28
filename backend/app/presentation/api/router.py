from fastapi import APIRouter

from app.presentation.api.v1 import (
    ai,
    auth,
    budgets,
    exports,
    goals,
    me,
    receipts,
    reminders,
    transactions,
)

api_router = APIRouter(prefix="/v1")
for module in (auth, me, goals, transactions, budgets, exports, receipts, reminders, ai):
    api_router.include_router(module.router)
