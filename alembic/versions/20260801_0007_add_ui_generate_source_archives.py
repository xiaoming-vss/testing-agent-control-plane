"""add UI generation source archives

Revision ID: 20260801_0007
Revises: 20260801_0006
Create Date: 2026-08-01 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260801_0007"
down_revision = "20260801_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_generate_task_source_archives",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("archive_id", sa.String(length=64), nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_generate_task_source_archives")),
        sa.UniqueConstraint(
            "archive_id", name=op.f("uq_ai_generate_task_source_archives_archive_id")
        ),
        sa.UniqueConstraint("task_id", name=op.f("uq_ai_generate_task_source_archives_task_id")),
    )


def downgrade() -> None:
    op.drop_table("ai_generate_task_source_archives")
