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
DYNAMODB_MODE=local \
DYNAMODB_ENDPOINT_URL=http://localhost:55000 \
uvicorn app.main:app --reload
```

Or without activation:

```shell
DYNAMODB_MODE=local \
DYNAMODB_ENDPOINT_URL=http://localhost:55000 \
uv run uvicorn app.main:app --reload
```

The same repository code can target AWS-hosted DynamoDB by setting `DYNAMODB_MODE=aws`
and leaving `DYNAMODB_ENDPOINT_URL` unset.

## Optional Remote Agent Services

Run the remote A2A Research Agent:

```shell
cd ../remote-agents/research-agent
uv run uvicorn app.main:app --reload --port 8101
```

Run the Sentiment MCP server:

```shell
cd ../mcp-servers/sentiment
uv run uvicorn app.main:app --reload --port 8201
```

The backend falls back to local behavior if either service is unavailable.

## Test

```shell
uv run pytest
```

## Generate schemas

```shell
uv run python scripts/generate_schemas.py
```
