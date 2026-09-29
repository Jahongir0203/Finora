from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.domain.common.values import MAX_AMOUNT, MAX_NAME_LENGTH, MAX_NOTE_LENGTH


class StrictModel(BaseModel):
    """Mass assignment himoyasi: noma'lum maydonlar (user_id, saved, ...) rad etiladi."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# Summa: faqat butun son, 0 < x <= 10^12 (float, "100" kabi satrlar rad etiladi)
Amount = Annotated[int, Field(strict=True, gt=0, le=MAX_AMOUNT)]
NonNegativeAmount = Annotated[int, Field(strict=True, ge=0, le=MAX_AMOUNT)]
Name = Annotated[str, StringConstraints(min_length=1, max_length=MAX_NAME_LENGTH)]
# Bo'sh bo'lishi mumkin — domen aniq xato kodi beradi (goal_name_required va h.k.)
LooseName = Annotated[str, StringConstraints(max_length=MAX_NAME_LENGTH)]
Note = Annotated[str, StringConstraints(max_length=MAX_NOTE_LENGTH)]
TxNote = Annotated[str, StringConstraints(max_length=256)]


class MessageOut(BaseModel):
    message: str


class ErrorOut(BaseModel):
    """Yagona xato formati (BE-1801). Qo'shimcha maydonlar koddan kelib chiqadi."""

    code: str
    message: str
    request_id: str | None
    fields: list[str] | None = None
    retry_after: int | None = None
    attempts_left: int | None = None


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorOut, "description": "unauthorized / token_expired / session_expired"},
    404: {"model": ErrorOut, "description": "not_found (begona resurs ham)"},
    422: {"model": ErrorOut, "description": "validation_error + fields[] va boshqa kodlar"},
    429: {"model": ErrorOut, "description": "rate_limited + retry_after"},
}
