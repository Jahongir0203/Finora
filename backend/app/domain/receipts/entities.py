from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Receipt:
    """Chek rasmi. Fayl yopiq omborda; ochish faqat 5 daqiqalik imzolangan URL orqali."""

    id: UUID
    user_id: UUID
    file_key: str
    content_type: str
    size_bytes: int
    created_at: datetime
