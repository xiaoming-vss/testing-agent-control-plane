"""add requirement document file metadata

Revision ID: 20260630_0003
Revises: 20260626_0002
Create Date: 2026-06-30
"""

import sqlalchemy as sa

from alembic import op

revision = "20260630_0003"
down_revision = "20260626_0002"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def _add_column_if_missing(table_name: str, existing: set[str], column: sa.Column) -> None:
    if column.name not in existing:
        op.add_column(table_name, column)


def upgrade() -> None:
    existing = _columns("requirements")
    _add_column_if_missing(
        "requirements",
        existing,
        sa.Column("document_filename", sa.String(length=255), nullable=False, server_default=""),
    )
    _add_column_if_missing(
        "requirements",
        existing,
        sa.Column("document_hash", sa.String(length=128), nullable=False, server_default=""),
    )
    _add_column_if_missing(
        "requirements",
        existing,
        sa.Column(
            "document_storage_path",
            sa.String(length=512),
            nullable=False,
            server_default="",
        ),
    )
    _add_column_if_missing(
        "requirements",
        existing,
        sa.Column(
            "document_download_url",
            sa.String(length=512),
            nullable=False,
            server_default="",
        ),
    )


def downgrade() -> None:
    existing = _columns("requirements")
    for column_name in (
        "document_download_url",
        "document_storage_path",
        "document_hash",
        "document_filename",
    ):
        if column_name in existing:
            op.drop_column("requirements", column_name)
