"""ORM modellari. Tashqi ID'lar UUIDv7, summalar BIGINT (so'm)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    LargeBinary,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, UTCDateTime


def _fk(target: str) -> ForeignKey:
    return ForeignKey(target, ondelete="CASCADE")

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    phone_ciphertext: Mapped[bytes] = mapped_column(LargeBinary)
    phone_index: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)


class DeviceModel(Base):
    __tablename__ = "devices"
    __table_args__ = (UniqueConstraint("user_id", "installation_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    installation_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    public_key: Mapped[bytes] = mapped_column(LargeBinary)
    name: Mapped[str] = mapped_column(String(64))
    platform: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    last_seen_at: Mapped[datetime] = mapped_column(UTCDateTime)
    # Push token faqat shu qurilmaga yuborish uchun; loglanmaydi, API'da qaytarilmaydi
    push_provider: Mapped[str | None] = mapped_column(String(8), nullable=True)
    push_token: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    device_id: Mapped[uuid.UUID] = mapped_column(_fk("devices.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    revoke_reason: Mapped[str | None] = mapped_column(String(32), nullable=True)


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        _fk("sessions.id"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime)
    used_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class GoalModel(Base):
    __tablename__ = "goals"
    __table_args__ = (CheckConstraint("target_amount > 0", name="target_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    target_amount: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)


class GoalEntryModel(Base):
    __tablename__ = "goal_entries"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("kind IN ('deposit', 'withdraw')", name="kind_valid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    goal_id: Mapped[uuid.UUID] = mapped_column(_fk("goals.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(16))
    amount: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)


class TransactionModel(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("kind IN ('income', 'expense')", name="kind_valid"),
        Index("ix_transactions_user_occurred", "user_id", "occurred_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"))
    kind: Mapped[str] = mapped_column(String(16))
    amount: Mapped[int] = mapped_column(BigInteger)
    category: Mapped[str] = mapped_column(String(64))
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(UTCDateTime)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)


class ExportModel(Base):
    __tablename__ = "exports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    file_key: Mapped[str] = mapped_column(String(255))
    download_token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
    downloaded_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class ReceiptModel(Base):
    __tablename__ = "receipts"
    __table_args__ = (CheckConstraint("size_bytes > 0", name="size_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    file_key: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(32))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)


class ReminderModel(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        CheckConstraint("amount IS NULL OR amount > 0", name="amount_positive"),
        CheckConstraint("repeat IN ('none', 'daily', 'weekly', 'monthly')", name="repeat_valid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(64))
    amount: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    due_at: Mapped[datetime] = mapped_column(UTCDateTime)
    repeat: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)


class BudgetModel(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("user_id", "category"),
        CheckConstraint("monthly_limit > 0", name="limit_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(64))
    monthly_limit: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)


class NotificationModel(Base):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_created", "user_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"))
    kind: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(128))
    body: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    read_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class IdempotencyKeyModel(Base):
    __tablename__ = "idempotency_keys"

    user_id: Mapped[uuid.UUID] = mapped_column(
        _fk("users.id"), primary_key=True
    )
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)


class AuditLogModel(Base):
    """Append-only. Ilova roli faqat INSERT huquqiga ega (deploy/db/post_migrate.sql).
    user_id'da FK yo'q — akkaunt o'chirilgandan keyin ham audit 1 yil saqlanadi."""

    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(32))
    device_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
