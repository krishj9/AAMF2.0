from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str | int | None = None
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


app = FastAPI(title="Sentiment MCP Server", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "server": "sentiment-mcp", "protocol": "MCP"}


@app.post("/mcp")
def mcp(request: JsonRpcRequest) -> dict[str, Any]:
    if request.method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "tools": [
                    {
                        "name": "analyze_symbol_news_sentiment",
                        "description": "Return deterministic synthetic sentiment for symbols.",
                    }
                ]
            },
        }

    if request.method == "tools/call":
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        if tool_name == "analyze_symbol_news_sentiment":
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": analyze_symbol_news_sentiment(arguments.get("symbols", [])),
            }

    return {
        "jsonrpc": "2.0",
        "id": request.id,
        "error": {"code": -32601, "message": "Method or tool not found"},
    }


def analyze_symbol_news_sentiment(symbols: list[str]) -> dict[str, Any]:
    stressed = any(symbol.upper() in {"BONDS", "FIXED_INCOME"} for symbol in symbols)
    sentiment = "CAUTIOUS" if stressed else "NEUTRAL"
    return {
        "symbols": symbols,
        "sentiment": sentiment,
        "score": -0.1 if stressed else 0.0,
        "summary": (
            f"MCP sentiment tool produced {sentiment.lower()} sentiment "
            f"for {', '.join(symbols)}."
        ),
    }
