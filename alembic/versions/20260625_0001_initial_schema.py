"""initial schema

Revision ID: 20260625_0001
Revises:
Create Date: 2026-06-25
"""

import testing_agent.models  # noqa: F401
from alembic import op
from testing_agent.models import Base

revision = "20260625_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
