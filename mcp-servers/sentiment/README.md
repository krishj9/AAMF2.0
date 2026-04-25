# Sentiment MCP Server

A minimal HTTP JSON-RPC MCP-style server exposing sentiment tools.

## Run

```shell
cd mcp-servers/sentiment
uv run uvicorn app.main:app --reload --port 8201
```

Endpoint: `POST /mcp`

Supported method:
- `tools/list`
- `tools/call` with `analyze_symbol_news_sentiment`
