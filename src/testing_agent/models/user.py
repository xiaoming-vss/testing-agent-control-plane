from __future__ import annotations

# ruff: noqa: F401
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from testing_agent.db.base import Base, CreatedAt, IdPk, UpdatedAt
from testing_agent.models.common import SoftDeleteMixin


class User(Base):
    __tablename__ = "users"
    id: Mapped[IdPk]
    user_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
