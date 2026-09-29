from typing import Any

from pydantic import BaseModel


class CurrencyOut(BaseModel):
    code: str
    symbol: str
    name: str
    rate_to_uzs: str | None
    rate_date: str | None


class FaqOut(BaseModel):
    id: str
    question: str
    answer: str


class ContactsOut(BaseModel):
    telegram: str
    phone: str
    email: str
    live_chat: bool


class SupportSessionOut(BaseModel):
    provider: str
    user_id: str
    user_hash: str


class SyncEntityOut(BaseModel):
    changed: list[dict[str, Any]]
    deleted: list[str]


class SyncOut(BaseModel):
    server_time: str
    has_more: bool
    transactions: SyncEntityOut
    goals: SyncEntityOut
    reminders: SyncEntityOut
    categories: SyncEntityOut
    accounts: SyncEntityOut
