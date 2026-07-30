"""add bug closed to sprint daily metrics

Revision ID: 20260729_0002
Revises: 20260729_0001
Create Date: 2026-07-29 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260729_0002"
down_revision = "20260729_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sprint_daily_metrics",
        sa.Column("bug_closed", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("sprint_daily_metrics", "bug_closed", server_default=None)


def downgrade() -> None:
    op.drop_column("sprint_daily_metrics", "bug_closed")
