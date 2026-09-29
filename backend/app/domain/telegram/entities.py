"""Telegram bot orqali OTP (o'z botimiz).

Bot foydalanuvchiga telefon raqami orqali yoza olmaydi — faqat `chat_id` orqali. Shuning uchun
foydalanuvchi botga bir marta O'Z raqamini ulashadi (`request_contact` tugmasi), backend
`raqam -> chat_id` bog'lanishini saqlaydi. Raqam ochiq saqlanmaydi — faqat HMAC blind index.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TelegramLink:
    phone_index: str
    chat_id: int
    telegram_user_id: int
    # Bot xabarlari tili (Telegram'dagi language_code'dan)
    language: str
    linked_at: datetime
