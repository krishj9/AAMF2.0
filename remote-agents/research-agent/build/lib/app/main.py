import os
from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field


class A2AResearchRequest(BaseModel):
    task: str
    request_id: str
    symbols: list[str] = Field(default_factory=list)
    portfolio_request: dict[str, Any] = Field(default_factory=dict)


class A2AResearchResponse(BaseModel):
    agent: str = "Research Agent"
    protocol: str = "A2A"
    request_id: str
    summary: str
    payload: dict[str, Any]


app = FastAPI(title="Remote Research Agent", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "agent": "research", "protocol": "A2A"}


@app.post("/a2a/research", response_model=A2AResearchResponse)
async def research(request: A2AResearchRequest) -> A2AResearchResponse:
    sentiment = await _call_sentiment_mcp(request.symbols)
    symbol_text = ", ".join(request.symbols) if request.symbols else "no symbols"
    return A2AResearchResponse(
        request_id=request.request_id,
        summary=f"Remote A2A research prepared context for {symbol_text}.",
        payload={
            "symbols": request.symbols,
            "market_context": "Synthetic A2A research context from request holdings.",
            "sentiment": sentiment,
            "source": "remote_a2a_research_agent",
        },
    )


async def _call_sentiment_mcp(symbols: list[str]) -> dict[str, Any]:
    mcp_url = os.getenv("SENTIMENT_MCP_URL", "http://localhost:8201/mcp")
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": "remote-research-sentiment",
                    "method": "tools/call",
                    "params": {
                        "name": "analyze_symbol_news_sentiment",
                        "arguments": {"symbols": symbols},
                    },
                },
            )
            response.raise_for_status()
            return response.json().get("result", {})
    except httpx.HTTPError:
        return {
            "sentiment": "NEUTRAL",
            "summary": "MCP sentiment server unavailable; remote research used neutral fallback.",
        }
