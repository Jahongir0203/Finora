from datetime import date

from pydantic import BaseModel, Field

from app.application.stats.use_cases import StatsPeriod


class BarOut(BaseModel):
    label: str
    value: int
    current: bool
    future: bool


class BreakdownOut(BaseModel):
    category_id: str
    amount: int
    pct: int


class StatsOut(BaseModel):
    period: StatsPeriod
    from_: date = Field(alias="from")
    to: date
    total_spent: int
    previous_total: int
    change_pct: int | None
    bars: list[BarOut]
    breakdown: list[BreakdownOut]
    has_enough_data: bool
    total_spent_display: str | None = None
    display_currency: str | None = None
