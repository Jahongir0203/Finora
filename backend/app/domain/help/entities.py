from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class FaqItem:
    """FAQ (BE-1701). Admin jadvalda tahrirlaydi; seed: `python -m app.seed`."""

    id: UUID
    language: str
    question: str
    answer: str
    position: int
