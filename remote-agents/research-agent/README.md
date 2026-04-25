# Remote Research Agent

A small A2A-style FastAPI service for portfolio research.

## Run

```shell
cd remote-agents/research-agent
uv run uvicorn app.main:app --reload --port 8101
```

The main backend calls `POST /a2a/research` when `RESEARCH_AGENT_REMOTE_ENABLED=true`.

## AWS Lambda

Lambda handler: `app.lambda_handler.handler`

Set `SENTIMENT_MCP_URL` to the deployed MCP endpoint, for example
`https://<api-id>.execute-api.<region>.amazonaws.com/mcp`.
