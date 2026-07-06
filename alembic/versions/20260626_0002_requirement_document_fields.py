"""add requirement document fields

Revision ID: 20260626_0002
Revises: 20260625_0001
Create Date: 2026-06-26
"""

import sqlalchemy as sa

from alembic import op

revision = "20260626_0002"
down_revision = "20260625_0001"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    existing = _columns("requirements")
    if "document_type" not in existing:
        op.add_column(
            "requirements",
            sa.Column(
                "document_type",
                sa.String(length=20),
                nullable=False,
                server_default="text",
            ),
        )
        op.alter_column("requirements", "document_type", server_default=None)
    if "document_content" not in existing:
        op.add_column(
            "requirements",
            sa.Column("document_content", sa.Text(), nullable=True),
        )
        op.execute("UPDATE requirements SET document_content = '' WHERE document_content IS NULL")


def downgrade() -> None:
    existing = _columns("requirements")
    if "document_content" in existing:
        op.drop_column("requirements", "document_content")
    if "document_type" in existing:
        op.drop_column("requirements", "document_type")
