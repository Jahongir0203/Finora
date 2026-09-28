from fastapi import APIRouter

from app.presentation.api.v1 import auth, exports, goals, me, transactions

api_router = APIRouter(prefix="/v1")
for module in (auth, me, goals, transactions, exports):
    api_router.include_router(module.router)
