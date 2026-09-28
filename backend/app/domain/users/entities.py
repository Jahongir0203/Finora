from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class User:
    id: UUID
    # Telefon field-level shifrlangan (AES-GCM); qidiruv faqat HMAC blind-index orqali
    phone_ciphertext: bytes
    phone_index: str
    created_at: datetime
