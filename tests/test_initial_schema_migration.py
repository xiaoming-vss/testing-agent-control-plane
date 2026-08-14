from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import sqlalchemy as sa

import testing_agent.models  # noqa: F401
from testing_agent.models import Base

MIGRATION_PATH = (
    Path(__file__).parents[1] / "alembic" / "versions" / "20260807_0001_initial_test_schema.py"
)


def _load_migration():
    spec = importlib.util.spec_from_file_location("initial_test_schema", MIGRATION_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RecordingOperations:
    def __init__(self) -> None:
        self.created_tables: dict[str, set[str]] = {}
        self.dropped_tables: list[str] = []

    def f(self, name: str) -> str:
        return name

    def create_table(self, name: str, *elements: Any, **_: Any) -> None:
        self.created_tables[name] = {
            element.name for element in elements if isinstance(element, sa.Column)
        }

    def create_index(self, *_: Any, **__: Any) -> None:
        pass

    def drop_index(self, *_: Any, **__: Any) -> None:
        pass

    def drop_table(self, name: str, **_: Any) -> None:
        self.dropped_tables.append(name)


def test_initial_revision_is_the_only_baseline():
    migration = _load_migration()

    assert migration.revision == "20260807_0001"
    assert migration.down_revision is None


def test_initial_upgrade_matches_current_model_tables_and_columns(monkeypatch):
    migration = _load_migration()
    operations = RecordingOperations()
    monkeypatch.setattr(migration, "op", operations)

    migration.upgrade()

    expected = {
        table_name: set(table.columns.keys()) for table_name, table in Base.metadata.tables.items()
    }
    assert operations.created_tables == expected


def test_initial_downgrade_removes_every_model_table(monkeypatch):
    migration = _load_migration()
    operations = RecordingOperations()
    monkeypatch.setattr(migration, "op", operations)

    migration.downgrade()

    assert set(operations.dropped_tables) == set(Base.metadata.tables)
    assert len(operations.dropped_tables) == len(Base.metadata.tables)
