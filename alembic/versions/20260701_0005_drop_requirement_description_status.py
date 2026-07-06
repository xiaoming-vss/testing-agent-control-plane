"""drop requirement description and status

Revision ID: 20260701_0005
Revises: 20260701_0004
Create Date: 2026-07-01
"""

import sqlalchemy as sa

from alembic import op

revision = "20260701_0005"
down_revision = "20260701_0004"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    existing = _columns("requirements")
    for column_name in ("status", "description"):
        if column_name in existing:
            op.drop_column("requirements", column_name)


def downgrade() -> None:
    pass
