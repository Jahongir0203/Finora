from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Export:
    """Tayyor eksport. 24 soatdan keyin o'chiriladi, yuklab olish havolasi bir martalik."""

    id: UUID
    user_id: UUID
    file_key: str
    download_token_hash: str
    created_at: datetime
    expires_at: datetime
    downloaded_at: datetime | None = None

    def is_downloadable(self, now: datetime) -> bool:
        return self.downloaded_at is None and now < self.expires_at
