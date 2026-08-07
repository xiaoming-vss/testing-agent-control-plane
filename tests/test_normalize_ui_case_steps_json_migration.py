import importlib.util
from pathlib import Path

import sqlalchemy as sa


def load_migration():
    path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "20260805_0009_normalize_ui_case_steps_json.py"
    )
    spec = importlib.util.spec_from_file_location("normalize_ui_case_steps_json", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_upgrade_converts_double_encoded_steps_and_preserves_arrays(monkeypatch):
    migration = load_migration()
    engine = sa.create_engine("sqlite://")
    metadata = sa.MetaData()
    cases = sa.Table(
        "ui_test_cases",
        metadata,
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("steps_json", sa.JSON(), nullable=False),
    )
    metadata.create_all(engine)
    legacy_steps = '[{"orderNo":1,"stepName":"登录","keyword":"open"}]'
    imported_steps = [{"orderNo": 1, "stepName": "打开登录页", "keyword": "open"}]

    with engine.begin() as connection:
        connection.execute(
            cases.insert(),
            [
                {"id": 1, "steps_json": legacy_steps},
                {"id": 2, "steps_json": imported_steps},
                {"id": 3, "steps_json": "not-json"},
            ],
        )
        monkeypatch.setattr(migration.op, "get_bind", lambda: connection)

        migration.upgrade()

        rows = connection.execute(sa.select(cases).order_by(cases.c.id)).mappings().all()

    assert rows[0]["steps_json"] == [{"orderNo": 1, "stepName": "登录", "keyword": "open"}]
    assert rows[1]["steps_json"] == imported_steps
    assert rows[2]["steps_json"] == "not-json"
