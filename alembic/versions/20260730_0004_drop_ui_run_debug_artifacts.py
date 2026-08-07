"""drop UI run URL and trace artifact fields

Revision ID: 20260730_0004
Revises: 20260729_0003
Create Date: 2026-07-30 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260730_0004"
down_revision = "20260729_0003"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    columns_by_table = {
        "ui_test_case_runs": ("current_url", "trace_path"),
        "ui_test_suite_runs": ("current_url", "trace_path"),
        "ui_test_suite_run_items": ("current_url",),
    }
    for table_name, column_names in columns_by_table.items():
        existing = _columns(table_name)
        for column_name in column_names:
            if column_name in existing:
                op.drop_column(table_name, column_name)


def downgrade() -> None:
    columns_by_table = {
        "ui_test_case_runs": ("current_url", "trace_path"),
        "ui_test_suite_runs": ("current_url", "trace_path"),
        "ui_test_suite_run_items": ("current_url",),
    }
    for table_name, column_names in columns_by_table.items():
        existing = _columns(table_name)
        for column_name in column_names:
            if column_name not in existing:
                op.add_column(
                    table_name,
                    sa.Column(
                        column_name,
                        sa.Text(),
                        nullable=False,
                        server_default="",
                    ),
                )
                op.alter_column(table_name, column_name, server_default=None)
