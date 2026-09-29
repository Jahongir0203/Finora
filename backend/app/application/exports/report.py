"""Eksport hisobotining tildan mustaqil ma'lumoti (renderer'lar shuni chizadi)."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ReportLabels:
    title: str
    period: str
    income: str
    expenses: str
    net: str
    by_category: str
    transactions: str
    summary: str
    col_date: str
    col_type: str
    col_category: str
    col_title: str
    col_amount: str
    col_note: str
    col_share: str


@dataclass(frozen=True, slots=True)
class ReportRow:
    date: str
    type: str
    category: str
    title: str
    amount: int  # chiqim manfiy, kirim musbat
    note: str


@dataclass(frozen=True, slots=True)
class CategoryLine:
    name: str
    amount: int
    pct: int


@dataclass(frozen=True, slots=True)
class ExportReport:
    labels: ReportLabels
    range_label: str
    income: int
    expenses: int
    net: int
    categories: list[CategoryLine] = field(default_factory=list)
    rows: list[ReportRow] = field(default_factory=list)
