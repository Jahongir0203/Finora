from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.exports.entities import ExportFormat, ExportPeriod, ExportStatus
from app.domain.transactions.entities import TransactionType
from app.presentation.schemas.common import StrictModel


class ExportCreateIn(StrictModel):
    period: ExportPeriod
    include: list[TransactionType] = Field(max_length=3)
    format: ExportFormat


class ExportPreviewOut(BaseModel):
    range_label: str
    from_: date = Field(alias="from")
    to: date
    count: int
    income: int
    expenses: int
    net: int
    file_name: str


class ExportOut(BaseModel):
    id: UUID
    status: ExportStatus
    file_name: str
    format: ExportFormat
    period: ExportPeriod
    download_url: str | None
    error_code: str | None
    row_count: int
    expires_at: datetime
