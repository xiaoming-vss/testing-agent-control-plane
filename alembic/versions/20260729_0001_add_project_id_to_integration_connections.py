"""add project id to integration connections

Revision ID: 20260729_0001
Revises: 20260701_0005
Create Date: 2026-07-29 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260729_0001"
down_revision = "20260701_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "integration_connections",
        sa.Column(
            "project_id",
            sa.String(length=64),
            nullable=False,
            server_default="",
        ),
    )
    op.create_index(
        op.f("ix_integration_connections_project_id"),
        "integration_connections",
        ["project_id"],
        unique=False,
    )
    op.drop_constraint(
        "uk_connection_user_provider_name",
        "integration_connections",
        type_="unique",
    )
    op.create_unique_constraint(
        "uk_connection_project_user_provider_name",
        "integration_connections",
        ["project_id", "user_id", "provider", "name"],
    )
    op.alter_column("integration_connections", "project_id", server_default=None)


def downgrade() -> None:
    op.drop_constraint(
        "uk_connection_project_user_provider_name",
        "integration_connections",
        type_="unique",
    )
    op.create_unique_constraint(
        "uk_connection_user_provider_name",
        "integration_connections",
        ["user_id", "provider", "name"],
    )
    op.drop_index(
        op.f("ix_integration_connections_project_id"),
        table_name="integration_connections",
    )
    op.drop_column("integration_connections", "project_id")
