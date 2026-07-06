from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class ResourceBinding(Base, SoftDeleteMixin):
    __tablename__ = "resource_bindings"
    __table_args__ = (
        Index("idx_binding_connection", "connection_id", "status"),
        Index("idx_binding_local", "user_id", "local_resource_type", "local_resource_id", "status"),
        Index(
            "idx_binding_remote", "provider", "remote_resource_type", "remote_resource_id", "status"
        ),
    )
    id: Mapped[IdPk]
    binding_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    connection_id: Mapped[str] = mapped_column(String(64), nullable=False)
    local_resource_type: Mapped[str] = mapped_column(String(30), nullable=False)
    local_resource_id: Mapped[str] = mapped_column(String(64), nullable=False)
    remote_resource_type: Mapped[str] = mapped_column(String(30), nullable=False)
    remote_resource_id: Mapped[str] = mapped_column(String(120), nullable=False)
    remote_parent_id: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    remote_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    bound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_sync_error: Mapped[str] = mapped_column(Text, nullable=False, default="")
    extra_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
