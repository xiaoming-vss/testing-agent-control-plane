"""add ui suite screenshot policy

Revision ID: 20260729_0003
Revises: 20260729_0002
Create Date: 2026-07-29 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260729_0003"
down_revision = "20260729_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ui_test_suites",
        sa.Column(
            "screenshot_policy",
            sa.String(length=32),
            nullable=False,
            server_default="on_failure",
        ),
    )
    op.alter_column("ui_test_suites", "screenshot_policy", server_default=None)


def downgrade() -> None:
    op.drop_column("ui_test_suites", "screenshot_policy")
