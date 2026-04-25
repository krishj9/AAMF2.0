# Remote Research Agent

A small A2A-style FastAPI service for portfolio research.

## Run

```shell
cd remote-agents/research-agent
uv run uvicorn app.main:app --reload --port 8101
```

The main backend calls `POST /a2a/research` when `RESEARCH_AGENT_REMOTE_ENABLED=true`.
