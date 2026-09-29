"""ORM modellari. Tashqi ID'lar UUIDv7, summalar BIGINT (so'm)."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    false,
    true,
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
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(8), server_default="uz-Latn")
    currency: Mapped[str] = mapped_column(String(3), server_default="UZS")
    theme: Mapped[str] = mapped_column(String(8), server_default="system")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, server_default=true())
    timezone: Mapped[str] = mapped_column(String(64), server_default="Asia/Tashkent")
    balance_set: Mapped[bool] = mapped_column(Boolean, server_default=false())


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
    has_pin_setup: Mapped[bool] = mapped_column(Boolean, server_default=false())
    auto_lock_minutes: Mapped[int] = mapped_column(Integer, server_default="1")
    biometric_enabled: Mapped[bool] = mapped_column(Boolean, server_default=false())
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)


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


class AccountModel(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("opening_balance >= 0", name="opening_non_negative"),
        CheckConstraint("type IN ('card', 'cash', 'bank_account')", name="type_valid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(16))
    name: Mapped[str] = mapped_column(String(64))
    bank_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    network: Mapped[str | None] = mapped_column(String(16), nullable=True)
    # To'liq karta raqami ustuni ataylab yo'q (BE-1401)
    last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    expiry: Mapped[str | None] = mapped_column(String(5), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    opening_balance: Mapped[int] = mapped_column(BigInteger)
    monthly_limit: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    frozen: Mapped[bool] = mapped_column(Boolean, server_default=false())
    is_default: Mapped[bool] = mapped_column(Boolean, server_default=false())
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
    archived_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class CategoryModel(Base):
    """Faqat user kategoriyalari. Tizim kategoriyalari kodda (app/domain/categories)."""

    __tablename__ = "categories"
    __table_args__ = (CheckConstraint("type IN ('expense', 'income')", name="type_valid"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(32))
    # Nom takrorini katta-kichik harfsiz tekshirish uchun (unique emas: soft delete bor)
    name_key: Mapped[str] = mapped_column(String(32))
    icon: Mapped[str] = mapped_column(String(32))
    color: Mapped[str] = mapped_column(String(7))
    type: Mapped[str] = mapped_column(String(8))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class CategoryPrefModel(Base):
    """Kategoriya limiti va nom override (tizim va user kategoriyalari uchun)."""

    __tablename__ = "category_prefs"

    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), primary_key=True)
    category_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    monthly_limit: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    name_override: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)


class GoalModel(Base):
    __tablename__ = "goals"
    __table_args__ = (CheckConstraint("target_amount > 0", name="target_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    target_amount: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    icon: Mapped[str] = mapped_column(String(32), server_default="target")
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    auto_save_monthly: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    auto_save_day: Mapped[int] = mapped_column(Integer, server_default="1")
    updated_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class GoalEntryModel(Base):
    __tablename__ = "goal_entries"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("kind IN ('deposit', 'withdraw')", name="kind_valid"),
        UniqueConstraint("goal_id", "dedupe_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    goal_id: Mapped[uuid.UUID] = mapped_column(_fk("goals.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(16))
    amount: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source: Mapped[str] = mapped_column(String(8), server_default="manual")
    dedupe_key: Mapped[str | None] = mapped_column(String(32), nullable=True)


class TransactionModel(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("type IN ('income', 'expense', 'transfer')", name="type_valid"),
        Index("ix_transactions_user_occurred", "user_id", "occurred_at"),
        Index("ix_transactions_user_category_occurred", "user_id", "category_id",
              "occurred_at"),
        Index("ix_transactions_user_updated", "user_id", "updated_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"))
    account_id: Mapped[uuid.UUID] = mapped_column(_fk("accounts.id"), index=True)
    type: Mapped[str] = mapped_column(String(16))
    amount: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(String(3), server_default="UZS")
    category_id: Mapped[str] = mapped_column(String(36))
    title: Mapped[str | None] = mapped_column(String(64), nullable=True)
    note: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source: Mapped[str] = mapped_column(String(8), server_default="manual")
    receipt_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("receipts.id", ondelete="SET NULL"), nullable=True
    )
    occurred_at: Mapped[datetime] = mapped_column(UTCDateTime)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)
    deleted_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    client_created_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    transfer_peer_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    direction: Mapped[str | None] = mapped_column(String(3), nullable=True)


class ExportModel(Base):
    __tablename__ = "exports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(8), index=True)
    period: Mapped[str] = mapped_column(String(8))
    format: Mapped[str] = mapped_column(String(4))
    include: Mapped[list[str]] = mapped_column(JSON)
    range_start: Mapped[date] = mapped_column(Date)
    range_end: Mapped[date] = mapped_column(Date)
    file_name: Mapped[str] = mapped_column(String(64))
    language: Mapped[str] = mapped_column(String(8))
    timezone: Mapped[str] = mapped_column(String(64))
    file_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, server_default="0")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    ready_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
    downloaded_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class ReceiptModel(Base):
    __tablename__ = "receipts"
    __table_args__ = (
        CheckConstraint("size_bytes IS NULL OR size_bytes > 0", name="size_positive"),
        UniqueConstraint("user_id", "fiscal_sign"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    source: Mapped[str] = mapped_column(String(8), server_default="image")
    file_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    merchant: Mapped[str | None] = mapped_column(String(128), nullable=True)
    total: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    occurred_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    suggested_category_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, server_default="0")
    fiscal_sign: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class ReminderModel(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("repeat IN ('once', 'weekly', 'monthly', 'yearly')",
                        name="repeat_valid"),
        Index("ix_reminders_due", "enabled", "next_due_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(64))
    category_id: Mapped[str] = mapped_column(String(36))
    amount: Mapped[int] = mapped_column(BigInteger)
    next_due_date: Mapped[date] = mapped_column(Date)
    anchor_day: Mapped[int] = mapped_column(Integer)
    repeat: Mapped[str] = mapped_column(String(16))
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=true())
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class NotificationModel(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_created", "user_id", "created_at"),
        UniqueConstraint("user_id", "dedupe_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"))
    type: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(128))
    body: Mapped[str] = mapped_column(String(512))
    deep_link: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    read_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    dedupe_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    push_status: Mapped[str] = mapped_column(String(8), server_default="none", index=True)
    push_attempts: Mapped[int] = mapped_column(Integer, server_default="0")
    push_title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    push_body: Mapped[str | None] = mapped_column(String(256), nullable=True)
    exclude_device_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    push_scope: Mapped[str] = mapped_column(String(8), server_default="active")


class InsightModel(Base):
    __tablename__ = "insights"
    __table_args__ = (UniqueConstraint("user_id", "dedupe_key"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(_fk("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(16))
    action: Mapped[str] = mapped_column(String(24))
    icon: Mapped[str] = mapped_column(String(32))
    category_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    saving: Mapped[int] = mapped_column(BigInteger)
    params: Mapped[dict[str, Any]] = mapped_column(JSON)
    extra: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(10))
    dedupe_key: Mapped[str] = mapped_column(String(96))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)


class FaqItemModel(Base):
    __tablename__ = "faq_items"
    __table_args__ = (Index("ix_faq_items_lang_pos", "language", "position"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    language: Mapped[str] = mapped_column(String(8))
    question: Mapped[str] = mapped_column(String(256))
    answer: Mapped[str] = mapped_column(String(2000))
    position: Mapped[int] = mapped_column(Integer)


class CurrencyRateModel(Base):
    __tablename__ = "currency_rates"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    rate_to_uzs: Mapped[Any] = mapped_column(Numeric(18, 4))
    rate_date: Mapped[date] = mapped_column(Date)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)


class TelegramLinkModel(Base):
    """Telegram bot OTP: raqam (blind index) -> chat. Raqamning o'zi saqlanmaydi."""

    __tablename__ = "telegram_links"

    phone_index: Mapped[str] = mapped_column(String(64), primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger)
    language: Mapped[str] = mapped_column(String(8))
    linked_at: Mapped[datetime] = mapped_column(UTCDateTime)


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
