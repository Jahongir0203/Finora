from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.presentation.schemas.common import StrictModel

Question = Annotated[str, StringConstraints(min_length=1, max_length=300)]


class AskIn(StrictModel):
    question: Question


class AskOut(BaseModel):
    answer: str
    window_days: int
