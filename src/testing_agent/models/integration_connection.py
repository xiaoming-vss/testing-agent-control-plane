from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class IntegrationConnection(Base, SoftDeleteMixin):
    __tablename__ = "integration_connections"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "name", name="uk_connection_user_provider_name"),
    )
    id: Mapped[IdPk]
    connection_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    base_url: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    auth_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    account: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    secret_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False, default="")
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="active")
    last_auth_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_auth_error: Mapped[str] = mapped_column(Text, nullable=False, default="")
    extra_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
