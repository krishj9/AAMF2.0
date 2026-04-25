# Asset Management Backend

FastAPI backend for the personal portfolio multi-agent platform.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python and dependency management.

## Local setup

```shell
cd backend
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Alternative: skip activation and use `uv run` (see below).

## Run

With an activated venv:

```shell
uvicorn app.main:app --reload
```

Or without activation:

```shell
uv run uvicorn app.main:app --reload
```

## Test

```shell
uv run pytest
```

## Generate schemas

```shell
uv run python scripts/generate_schemas.py
```
