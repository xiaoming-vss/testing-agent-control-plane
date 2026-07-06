# testing-agent-control-plane

Python control-plane rewrite for `testing-agent`.

## Scope

This project rewrites the Go backend control plane only. Worker executors stay outside this repository. The backend keeps the existing `/v1` and `/internal/*-worker` contracts so existing frontends and workers can keep talking to it.

## Stack

- Python 3.12
- uv
- FastAPI
- SQLAlchemy 2.x async ORM
- Alembic migrations
- Pydantic v2
- MySQL via asyncmy

## Local configuration

Create a local config from the example:

```powershell
Copy-Item config/local.example.toml config/local.toml
```

The example config points at:

```text
127.0.0.1:3306/testing-agent-python
user: root
password: password
```

## Commands

```powershell
uv sync --extra dev
uv run alembic upgrade head
uv run testing-agent-control-plane --config config/local.toml
uv run pytest
```

## Storage

Project skill files are stored under `storage/skills/`. The directory is kept in
the repository with `.gitkeep`; uploaded/generated skill archives should live
there at runtime.
