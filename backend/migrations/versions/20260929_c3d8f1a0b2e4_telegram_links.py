"""telegram links (OTP o'z bot orqali)

Revision ID: c3d8f1a0b2e4
Revises: b7c1e4d2a9f0
Create Date: 2026-09-29 12:00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3d8f1a0b2e4"
down_revision: str | Sequence[str] | None = "b7c1e4d2a9f0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "telegram_links",
        sa.Column("phone_index", sa.String(64), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("phone_index", name=op.f("pk_telegram_links")),
        sa.UniqueConstraint("chat_id", name=op.f("uq_telegram_links_chat_id")),
    )


def downgrade() -> None:
    op.drop_table("telegram_links")
