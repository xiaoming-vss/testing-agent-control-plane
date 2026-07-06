from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class ApiEnvironmentVar(Base):
    __tablename__ = "api_environment_vars"
    __table_args__ = (UniqueConstraint("environment_id", "var_key", name="uk_api_env_var_key"),)
    id: Mapped[IdPk]
    env_var_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    environment_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    var_key: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    is_secret: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
