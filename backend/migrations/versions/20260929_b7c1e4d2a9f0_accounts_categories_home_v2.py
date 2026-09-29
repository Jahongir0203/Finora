"""accounts, categories, transactions v2, exports async, insights, faq, rates (Backend_task.md)

Revision ID: b7c1e4d2a9f0
Revises: 5a24b90a75ad
Create Date: 2026-09-29 10:00:00

Ma'lumotlar saqlanadi:
- Har bir tranzaksiyasi bor userga "Cash" (standart) hisob yaratiladi, tranzaksiyalar unga
  bog'lanadi.
- Erkin matnli `category` tizim kategoriyasiga (id yoki en/uz/ru nomi bo'yicha) yoki shu nomli
  yangi user kategoriyasiga o'tkaziladi; eski `budgets` limitlari `category_prefs`ga ko'chadi.
- Eslatmalar: due_at -> next_due_date (Toshkent sanasi); summasiz eslatmalar 1 so'm bilan
  o'chirilgan holatda qoladi; `none` -> `once`, `daily` -> `weekly`.
- Bildirishnomalar: eski turlar -> `security`.
- Eksportlar: 24 soatlik vaqtinchalik yozuvlar — jadval qayta yaratiladi (oldin
  `python -m app.jobs purge` ishga tushirish tavsiya etiladi).
- Mavjud cheklar tasdiqlangan deb belgilanadi (24 soatlik tozalashga tushmasin).
"""
import os
import time
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta, timezone

import sqlalchemy as sa
from alembic import op

revision: str = "b7c1e4d2a9f0"
down_revision: str | Sequence[str] | None = "5a24b90a75ad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TZ = timezone(timedelta(hours=5))
_TS = sa.DateTime(timezone=True)

# Eski erkin matn -> tizim kategoriyasi (id, en/uz/ru nomlari, katta-kichik harfsiz)
_SYSTEM_ALIASES = {
    "groceries": ("groceries", "oziq-ovqat", "продукты"),
    "food": ("food", "food & drinks", "kafe va restoran", "кафе и рестораны", "ovqat"),
    "transport": ("transport", "транспорт", "taksi", "taxi"),
    "bills": ("bills", "kommunal to'lovlar", "счета и коммунальные", "kommunal"),
    "health": ("health", "salomatlik", "здоровье"),
    "shopping": ("shopping", "xaridlar", "покупки"),
    "housing": ("housing", "uy-joy", "жильё"),
    "subs": ("subs", "subscriptions", "obunalar", "подписки"),
    "salary": ("salary", "maosh", "зарплата"),
    "transfer": ("transfer", "transfers", "o'tkazmalar", "переводы"),
}
_ALIAS = {alias: cid for cid, names in _SYSTEM_ALIASES.items() for alias in names}
_INCOME = {"salary", "transfer"}


def _uuid7() -> uuid.UUID:
    ts_ms = time.time_ns() // 1_000_000
    rand = int.from_bytes(os.urandom(10), "big")
    value = (ts_ms & ((1 << 48) - 1)) << 80 | 0x7 << 76 | (rand >> 62 & 0xFFF) << 64
    return uuid.UUID(int=value | 0b10 << 62 | rand & ((1 << 62) - 1))


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid(value: object) -> uuid.UUID:
    """Xom SQL natijasi: Postgres — UUID, SQLite — 32 belgili hex satr."""
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


def _dt(value: object) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    assert isinstance(value, datetime)
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def _cols(*spec: tuple[str, sa.types.TypeEngine[object]]) -> list[sa.ColumnClause[object]]:
    return [sa.column(name, type_) for name, type_ in spec]


_U, _S, _B, _I = sa.Uuid(), sa.String(), sa.Boolean(), sa.BigInteger()


def _is_pg() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    bind = op.get_bind()

    # --- users / devices ------------------------------------------------------------------
    with op.batch_alter_table("users") as b:
        b.add_column(sa.Column("first_name", sa.String(64), nullable=True))
        b.add_column(sa.Column("last_name", sa.String(64), nullable=True))
        b.add_column(sa.Column("language", sa.String(8), server_default="uz-Latn",
                               nullable=False))
        b.add_column(sa.Column("currency", sa.String(3), server_default="UZS", nullable=False))
        b.add_column(sa.Column("theme", sa.String(8), server_default="system", nullable=False))
        b.add_column(sa.Column("notifications_enabled", sa.Boolean(), server_default=sa.true(),
                               nullable=False))
        b.add_column(sa.Column("timezone", sa.String(64), server_default="Asia/Tashkent",
                               nullable=False))
        b.add_column(sa.Column("balance_set", sa.Boolean(), server_default=sa.false(),
                               nullable=False))
    with op.batch_alter_table("devices") as b:
        b.add_column(sa.Column("has_pin_setup", sa.Boolean(), server_default=sa.false(),
                               nullable=False))
        b.add_column(sa.Column("auto_lock_minutes", sa.Integer(), server_default="1",
                               nullable=False))
        b.add_column(sa.Column("biometric_enabled", sa.Boolean(), server_default=sa.false(),
                               nullable=False))
        b.add_column(sa.Column("city", sa.String(64), nullable=True))

    # --- yangi jadvallar -------------------------------------------------------------------
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(16), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("bank_name", sa.String(64), nullable=True),
        sa.Column("network", sa.String(16), nullable=True),
        sa.Column("last4", sa.String(4), nullable=True),
        sa.Column("expiry", sa.String(5), nullable=True),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("opening_balance", sa.BigInteger(), nullable=False),
        sa.Column("monthly_limit", sa.BigInteger(), nullable=True),
        sa.Column("frozen", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", _TS, nullable=False),
        sa.Column("updated_at", _TS, nullable=False),
        sa.Column("archived_at", _TS, nullable=True),
        sa.CheckConstraint("opening_balance >= 0", name=op.f("ck_accounts_opening_non_negative")),
        sa.CheckConstraint("type IN ('card', 'cash', 'bank_account')",
                           name=op.f("ck_accounts_type_valid")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_accounts_user_id_users"),
                                ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
    )
    op.create_index(op.f("ix_accounts_user_id"), "accounts", ["user_id"])
    op.create_index(op.f("ix_accounts_updated_at"), "accounts", ["updated_at"])

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(32), nullable=False),
        sa.Column("name_key", sa.String(32), nullable=False),
        sa.Column("icon", sa.String(32), nullable=False),
        sa.Column("color", sa.String(7), nullable=False),
        sa.Column("type", sa.String(8), nullable=False),
        sa.Column("created_at", _TS, nullable=False),
        sa.Column("updated_at", _TS, nullable=False),
        sa.Column("deleted_at", _TS, nullable=True),
        sa.CheckConstraint("type IN ('expense', 'income')", name=op.f("ck_categories_type_valid")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],
                                name=op.f("fk_categories_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
    )
    op.create_index(op.f("ix_categories_user_id"), "categories", ["user_id"])
    op.create_index(op.f("ix_categories_updated_at"), "categories", ["updated_at"])

    op.create_table(
        "category_prefs",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.String(36), nullable=False),
        sa.Column("monthly_limit", sa.BigInteger(), nullable=True),
        sa.Column("name_override", sa.String(32), nullable=True),
        sa.Column("updated_at", _TS, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],
                                name=op.f("fk_category_prefs_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "category_id", name=op.f("pk_category_prefs")),
    )

    op.create_table(
        "insights",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("action", sa.String(24), nullable=False),
        sa.Column("icon", sa.String(32), nullable=False),
        sa.Column("category_id", sa.String(36), nullable=True),
        sa.Column("saving", sa.BigInteger(), nullable=False),
        sa.Column("params", sa.JSON(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("dedupe_key", sa.String(96), nullable=False),
        sa.Column("created_at", _TS, nullable=False),
        sa.Column("updated_at", _TS, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_insights_user_id_users"),
                                ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_insights")),
        sa.UniqueConstraint("user_id", "dedupe_key", name=op.f("uq_insights_user_id")),
    )
    op.create_index(op.f("ix_insights_user_id"), "insights", ["user_id"])

    op.create_table(
        "faq_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("question", sa.String(256), nullable=False),
        sa.Column("answer", sa.String(2000), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_faq_items")),
    )
    op.create_index("ix_faq_items_lang_pos", "faq_items", ["language", "position"])

    op.create_table(
        "currency_rates",
        sa.Column("code", sa.String(3), nullable=False),
        sa.Column("rate_to_uzs", sa.Numeric(18, 4), nullable=False),
        sa.Column("rate_date", sa.Date(), nullable=False),
        sa.Column("updated_at", _TS, nullable=False),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_currency_rates")),
    )

    # --- kategoriyalar: eski matn -> id -----------------------------------------------------
    cats = sa.table("categories", *_cols(
        ("id", _U), ("user_id", _U), ("name", _S), ("name_key", _S), ("icon", _S),
        ("color", _S), ("type", _S), ("created_at", _TS), ("updated_at", _TS)))
    created: dict[tuple[uuid.UUID, str], str] = {}

    def category_id(user_id: uuid.UUID, text: str, is_income: bool) -> str:
        key = text.strip().casefold()
        if key in _ALIAS:
            return _ALIAS[key]
        if (user_id, key) not in created:
            new_id = _uuid7()
            now = _now()
            name = text.strip()[:32] or "Other"
            op.bulk_insert(cats, [{
                "id": new_id, "user_id": user_id, "name": name, "name_key": name.casefold(),
                "icon": "briefcase" if is_income else "receipt",
                "color": "#10B981" if is_income else "#6366F1",
                "type": "income" if is_income else "expense",
                "created_at": now, "updated_at": now}])
            created[(user_id, key)] = str(new_id)
        return created[(user_id, key)]

    # --- transactions ----------------------------------------------------------------------
    old_tx = bind.execute(sa.text(
        "SELECT id, user_id, kind, category, created_at FROM transactions")).all()
    with op.batch_alter_table("transactions") as b:
        b.add_column(sa.Column("account_id", sa.Uuid(), nullable=True))
        b.add_column(sa.Column("type", sa.String(16), nullable=True))
        b.add_column(sa.Column("currency", sa.String(3), server_default="UZS", nullable=False))
        b.add_column(sa.Column("category_id", sa.String(36), nullable=True))
        b.add_column(sa.Column("title", sa.String(64), nullable=True))
        b.add_column(sa.Column("source", sa.String(8), server_default="manual", nullable=False))
        b.add_column(sa.Column("receipt_id", sa.Uuid(), nullable=True))
        b.add_column(sa.Column("updated_at", _TS, nullable=True))
        b.add_column(sa.Column("deleted_at", _TS, nullable=True))
        b.add_column(sa.Column("client_created_at", _TS, nullable=True))
        b.add_column(sa.Column("transfer_peer_id", sa.Uuid(), nullable=True))
        b.add_column(sa.Column("direction", sa.String(3), nullable=True))

    accounts = sa.table("accounts", *_cols(
        ("id", _U), ("user_id", _U), ("type", _S), ("name", _S), ("opening_balance", _I),
        ("is_default", _B), ("created_at", _TS), ("updated_at", _TS)))
    cash: dict[uuid.UUID, uuid.UUID] = {}
    tx = sa.table("transactions", *_cols(
        ("id", _U), ("account_id", _U), ("type", _S), ("category_id", _S),
        ("updated_at", _TS)))
    for raw_id, raw_user, kind, category, created_at in old_tx:
        tx_id, user_id = _uuid(raw_id), _uuid(raw_user)
        if user_id not in cash:
            cash[user_id] = _uuid7()
            now = _now()
            op.bulk_insert(accounts, [{
                "id": cash[user_id], "user_id": user_id, "type": "cash", "name": "Cash",
                "opening_balance": 0, "is_default": True, "created_at": now,
                "updated_at": now}])
        bind.execute(tx.update().where(tx.c.id == tx_id).values(
            account_id=cash[user_id], type=kind,
            category_id=category_id(user_id, category, kind == "income"),
            updated_at=_dt(created_at)))

    with op.batch_alter_table("transactions") as b:
        b.alter_column("account_id", existing_type=sa.Uuid(), nullable=False)
        b.alter_column("type", existing_type=sa.String(16), nullable=False)
        b.alter_column("category_id", existing_type=sa.String(36), nullable=False)
        b.alter_column("updated_at", existing_type=_TS, nullable=False)
        b.alter_column("note", existing_type=sa.String(255), type_=sa.String(256))
        b.drop_constraint(op.f("ck_transactions_kind_valid"), type_="check")
        b.drop_column("kind")
        b.drop_column("category")
        b.create_check_constraint("type_valid", "type IN ('income', 'expense', 'transfer')")
        b.create_foreign_key(op.f("fk_transactions_account_id_accounts"), "accounts",
                             ["account_id"], ["id"], ondelete="CASCADE")
        b.create_foreign_key(op.f("fk_transactions_receipt_id_receipts"), "receipts",
                             ["receipt_id"], ["id"], ondelete="SET NULL")
        b.create_index(op.f("ix_transactions_account_id"), ["account_id"])
        b.create_index("ix_transactions_user_category_occurred",
                       ["user_id", "category_id", "occurred_at"])
        b.create_index("ix_transactions_user_updated", ["user_id", "updated_at"])
    if _is_pg():
        # Activity qidiruvi (BE-503): pg_trgm (roles.sql'da superuser yaratadi)
        has_trgm = bind.execute(sa.text(
            "SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'")).scalar()
        if has_trgm:
            op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_title_trgm ON transactions "
                       "USING gin (title gin_trgm_ops)")
            op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_note_trgm ON transactions "
                       "USING gin (note gin_trgm_ops)")

    # --- budgets -> category_prefs -----------------------------------------------------------
    prefs = sa.table("category_prefs", *_cols(
        ("user_id", _U), ("category_id", _S), ("monthly_limit", _I), ("updated_at", _TS)))
    seen: set[tuple[uuid.UUID, str]] = set()
    for raw_user, category, limit in bind.execute(sa.text(
            "SELECT user_id, category, monthly_limit FROM budgets")).all():
        user_id = _uuid(raw_user)
        cid = category_id(user_id, category, False)
        if (user_id, cid) not in seen and cid not in _INCOME:
            seen.add((user_id, cid))
            op.bulk_insert(prefs, [{"user_id": user_id, "category_id": cid,
                                    "monthly_limit": limit, "updated_at": _now()}])
    op.drop_index(op.f("ix_budgets_user_id"), table_name="budgets")
    op.drop_table("budgets")

    # --- goals / goal_entries -------------------------------------------------------------
    with op.batch_alter_table("goals") as b:
        b.add_column(sa.Column("icon", sa.String(32), server_default="target", nullable=False))
        b.add_column(sa.Column("deadline", sa.Date(), nullable=True))
        b.add_column(sa.Column("auto_save_monthly", sa.BigInteger(), nullable=True))
        b.add_column(sa.Column("auto_save_day", sa.Integer(), server_default="1",
                               nullable=False))
        b.add_column(sa.Column("updated_at", _TS, nullable=True))
        b.add_column(sa.Column("deleted_at", _TS, nullable=True))
        b.create_index(op.f("ix_goals_updated_at"), ["updated_at"])
    op.execute("UPDATE goals SET updated_at = created_at")
    with op.batch_alter_table("goal_entries") as b:
        b.add_column(sa.Column("account_id", sa.Uuid(), nullable=True))
        b.add_column(sa.Column("source", sa.String(8), server_default="manual", nullable=False))
        b.add_column(sa.Column("dedupe_key", sa.String(32), nullable=True))
        b.create_foreign_key(op.f("fk_goal_entries_account_id_accounts"), "accounts",
                             ["account_id"], ["id"], ondelete="SET NULL")
        b.create_index(op.f("ix_goal_entries_account_id"), ["account_id"])
        b.create_unique_constraint(op.f("uq_goal_entries_goal_id"), ["goal_id", "dedupe_key"])

    # --- reminders -------------------------------------------------------------------------
    old_rem = bind.execute(sa.text(
        "SELECT id, amount, due_at, repeat, created_at FROM reminders")).all()
    with op.batch_alter_table("reminders") as b:
        b.add_column(sa.Column("category_id", sa.String(36), server_default="bills",
                               nullable=False))
        b.add_column(sa.Column("next_due_date", sa.Date(), nullable=True))
        b.add_column(sa.Column("anchor_day", sa.Integer(), nullable=True))
        b.add_column(sa.Column("enabled", sa.Boolean(), server_default=sa.true(),
                               nullable=False))
        b.add_column(sa.Column("updated_at", _TS, nullable=True))
        b.add_column(sa.Column("deleted_at", _TS, nullable=True))
        b.drop_constraint(op.f("ck_reminders_repeat_valid"), type_="check")
        b.drop_constraint(op.f("ck_reminders_amount_positive"), type_="check")
    rem = sa.table("reminders", *_cols(
        ("id", _U), ("amount", _I), ("next_due_date", sa.Date()), ("anchor_day", sa.Integer()),
        ("repeat", _S), ("enabled", _B), ("updated_at", _TS)))
    repeat_map = {"none": "once", "daily": "weekly", "weekly": "weekly", "monthly": "monthly"}
    for rid, amount, due_at, repeat, created_at in old_rem:
        local = _dt(due_at).astimezone(_TZ).date()
        bind.execute(rem.update().where(rem.c.id == _uuid(rid)).values(
            amount=amount or 1, next_due_date=local, anchor_day=local.day,
            repeat=repeat_map.get(repeat, "once"), enabled=amount is not None,
            updated_at=_dt(created_at)))
    with op.batch_alter_table("reminders") as b:
        b.alter_column("amount", existing_type=sa.BigInteger(), nullable=False)
        b.alter_column("next_due_date", existing_type=sa.Date(), nullable=False)
        b.alter_column("anchor_day", existing_type=sa.Integer(), nullable=False)
        b.alter_column("updated_at", existing_type=_TS, nullable=False)
        b.drop_column("due_at")
        b.create_check_constraint("repeat_valid",
                                  "repeat IN ('once', 'weekly', 'monthly', 'yearly')")
        b.create_check_constraint("amount_positive", "amount > 0")
        b.create_index("ix_reminders_due", ["enabled", "next_due_date"])
        b.create_index(op.f("ix_reminders_updated_at"), ["updated_at"])

    # --- notifications ---------------------------------------------------------------------
    with op.batch_alter_table("notifications") as b:
        b.add_column(sa.Column("type", sa.String(32), server_default="security",
                               nullable=False))
        b.add_column(sa.Column("deep_link", sa.String(64), nullable=True))
        b.add_column(sa.Column("deleted_at", _TS, nullable=True))
        b.add_column(sa.Column("dedupe_key", sa.String(128), nullable=True))
        b.add_column(sa.Column("push_status", sa.String(8), server_default="none",
                               nullable=False))
        b.add_column(sa.Column("push_attempts", sa.Integer(), server_default="0",
                               nullable=False))
        b.add_column(sa.Column("push_title", sa.String(128), nullable=True))
        b.add_column(sa.Column("push_body", sa.String(256), nullable=True))
        b.add_column(sa.Column("exclude_device_id", sa.Uuid(), nullable=True))
        b.add_column(sa.Column("push_scope", sa.String(8), server_default="active",
                               nullable=False))
    op.execute("UPDATE notifications SET deep_link = '/profile'")
    with op.batch_alter_table("notifications") as b:
        b.drop_column("kind")
        b.create_unique_constraint(op.f("uq_notifications_user_id"), ["user_id", "dedupe_key"])
        b.create_index(op.f("ix_notifications_push_status"), ["push_status"])

    # --- receipts --------------------------------------------------------------------------
    with op.batch_alter_table("receipts") as b:
        b.add_column(sa.Column("source", sa.String(8), server_default="image", nullable=False))
        b.add_column(sa.Column("merchant", sa.String(128), nullable=True))
        b.add_column(sa.Column("total", sa.BigInteger(), nullable=True))
        b.add_column(sa.Column("occurred_at", _TS, nullable=True))
        b.add_column(sa.Column("items", sa.JSON(), nullable=True))
        b.add_column(sa.Column("suggested_category_id", sa.String(36), nullable=True))
        b.add_column(sa.Column("confidence", sa.Float(), server_default="0", nullable=False))
        b.add_column(sa.Column("fiscal_sign", sa.String(64), nullable=True))
        b.add_column(sa.Column("confirmed_at", _TS, nullable=True))
        b.alter_column("file_key", existing_type=sa.String(255), nullable=True)
        b.alter_column("content_type", existing_type=sa.String(32), nullable=True)
        b.alter_column("size_bytes", existing_type=sa.BigInteger(), nullable=True)
        b.drop_constraint(op.f("ck_receipts_size_positive"), type_="check")
    op.execute("UPDATE receipts SET confirmed_at = created_at, items = '[]'")
    with op.batch_alter_table("receipts") as b:
        b.alter_column("items", existing_type=sa.JSON(), nullable=False)
        b.create_check_constraint("size_positive", "size_bytes IS NULL OR size_bytes > 0")
        b.create_unique_constraint(op.f("uq_receipts_user_id"), ["user_id", "fiscal_sign"])
        b.create_index(op.f("ix_receipts_created_at"), ["created_at"])

    # --- exports (vaqtinchalik yozuvlar — qayta yaratiladi) ---------------------------------
    op.drop_index(op.f("ix_exports_expires_at"), table_name="exports")
    op.drop_index(op.f("ix_exports_user_id"), table_name="exports")
    op.drop_table("exports")
    op.create_table(
        "exports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(8), nullable=False),
        sa.Column("period", sa.String(8), nullable=False),
        sa.Column("format", sa.String(4), nullable=False),
        sa.Column("include", sa.JSON(), nullable=False),
        sa.Column("range_start", sa.Date(), nullable=False),
        sa.Column("range_end", sa.Date(), nullable=False),
        sa.Column("file_name", sa.String(64), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("file_key", sa.String(255), nullable=True),
        sa.Column("error_code", sa.String(32), nullable=True),
        sa.Column("row_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", _TS, nullable=False),
        sa.Column("ready_at", _TS, nullable=True),
        sa.Column("expires_at", _TS, nullable=False),
        sa.Column("downloaded_at", _TS, nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_exports_user_id_users"),
                                ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exports")),
    )
    op.create_index(op.f("ix_exports_expires_at"), "exports", ["expires_at"])
    op.create_index(op.f("ix_exports_status"), "exports", ["status"])
    op.create_index(op.f("ix_exports_user_id"), "exports", ["user_id"])


def downgrade() -> None:
    raise NotImplementedError(
        "Ma'lumot tuzilmasi o'zgargan (hisoblar, kategoriyalar). Orqaga qaytarish — zaxiradan."
    )
