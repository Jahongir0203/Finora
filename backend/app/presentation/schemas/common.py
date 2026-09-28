from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.domain.common.values import MAX_AMOUNT, MAX_NAME_LENGTH, MAX_NOTE_LENGTH


class StrictModel(BaseModel):
    """Mass assignment himoyasi: noma'lum maydonlar (user_id, saved, ...) rad etiladi."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# Summa: faqat butun son, 0 < x <= 10^12 (float, "100" kabi satrlar rad etiladi)
Amount = Annotated[int, Field(strict=True, gt=0, le=MAX_AMOUNT)]
Name = Annotated[str, StringConstraints(min_length=1, max_length=MAX_NAME_LENGTH)]
Note = Annotated[str, StringConstraints(max_length=MAX_NOTE_LENGTH)]


class MessageOut(BaseModel):
    message: str
