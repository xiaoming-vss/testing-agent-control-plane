"""normalize UI case steps JSON arrays

Revision ID: 20260805_0009
Revises: 20260801_0008
Create Date: 2026-08-05 00:00:00.000000
"""

from __future__ import annotations

import json

import sqlalchemy as sa

from alembic import op

revision = "20260805_0009"
down_revision = "20260801_0008"
branch_labels = None
depends_on = None

CASES_TABLE = "ui_test_cases"


def upgrade() -> None:
    connection = op.get_bind()
    cases = sa.table(
        CASES_TABLE,
        sa.column("id", sa.BigInteger()),
        sa.column("steps_json", sa.JSON()),
    )
    rows = connection.execute(sa.select(cases.c.id, cases.c.steps_json)).mappings().all()
    for row in rows:
        value = row["steps_json"]
        if not isinstance(value, str):
            continue
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, list):
            continue
        connection.execute(
            sa.update(cases).where(cases.c.id == row["id"]).values(steps_json=parsed)
        )


def downgrade() -> None:
    # Array is the canonical storage type; reverting the code must not double-encode valid data.
    pass
