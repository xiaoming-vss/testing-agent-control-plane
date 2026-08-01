"""drop legacy imported collection field

Revision ID: 20260801_0008
Revises: 20260801_0007
Create Date: 2026-08-01 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260801_0008"
down_revision = "20260801_0007"
branch_labels = None
depends_on = None

RUNS_TABLE = "api_case_generate_task_runs"
LEGACY_INDEX = "ix_api_case_generate_task_runs_imported_collection_id"


def upgrade() -> None:
    op.drop_index(op.f(LEGACY_INDEX), table_name=RUNS_TABLE)
    op.drop_column(RUNS_TABLE, "imported_collection_id")


def downgrade() -> None:
    op.add_column(
        RUNS_TABLE,
        sa.Column(
            "imported_collection_id",
            sa.String(length=64),
            nullable=False,
            server_default="",
        ),
    )
    op.create_index(op.f(LEGACY_INDEX), RUNS_TABLE, ["imported_collection_id"], unique=False)
