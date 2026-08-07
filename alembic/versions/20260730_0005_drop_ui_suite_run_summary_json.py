"""drop UI suite run summary json

Revision ID: 20260730_0005
Revises: 20260730_0004
Create Date: 2026-07-30 00:05:00.000000
"""

from __future__ import annotations

from collections.abc import Iterable

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260730_0005"
down_revision = "20260730_0004"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _drop_columns(table_name: str, column_names: Iterable[str]) -> None:
    existing = _columns(table_name)
    with op.batch_alter_table(table_name) as batch_op:
        for column_name in column_names:
            if column_name in existing:
                batch_op.drop_column(column_name)


def _add_columns(table_name: str, columns: Iterable[sa.Column]) -> None:
    existing = _columns(table_name)
    with op.batch_alter_table(table_name) as batch_op:
        for column in columns:
            if column.name not in existing:
                batch_op.add_column(column)


def upgrade() -> None:
    _drop_columns("ui_test_suite_runs", ["summary_json"])


def downgrade() -> None:
    _add_columns(
        "ui_test_suite_runs",
        [
            sa.Column("summary_json", sa.JSON(), nullable=True),
        ],
    )