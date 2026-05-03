import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field

# Add backend to path so we can reuse the Bedrock adapter
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

logger = logging.getLogger(__name__)


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
    return {"status": "healthy", "agent": "Research Agent", "protocol": "A2A", "timestamp": __import__("datetime").datetime.now().isoformat()}


@app.post("/a2a/research", response_model=A2AResearchResponse)
async def research(request: A2AResearchRequest) -> A2AResearchResponse:
    symbol_text = ", ".join(request.symbols) if request.symbols else "no symbols"

    # Extract portfolio context from the request envelope
    portfolio_req = request.portfolio_request
    current_allocation = _extract_current_allocation(portfolio_req)
    rebalance_signal = _extract_rebalance_signal(portfolio_req)

    # Try LLM-enhanced research first
    llm_result = await _run_llm_research(request.symbols, current_allocation, rebalance_signal)

    if llm_result:
        return A2AResearchResponse(
            request_id=request.request_id,
            summary=f"LLM market research completed for {symbol_text}.",
            payload={
                "symbols": request.symbols,
                "market_context": llm_result.get("market_context", ""),
                "key_insights": llm_result.get("key_insights", []),
                "regime": llm_result.get("regime", "NEUTRAL"),
                "confidence": llm_result.get("confidence", 0.7),
                "source": "bedrock_llm",
            },
        )

    # Fallback: call sentiment MCP and return structured context
    sentiment = await _call_sentiment_mcp(request.symbols)
    return A2AResearchResponse(
        request_id=request.request_id,
        summary=f"Using request-provided market values for {symbol_text}.",
        payload={
            "symbols": request.symbols,
            "market_context": f"Portfolio holds {symbol_text}. Current allocation: {current_allocation}.",
            "key_insights": [
                f"Rebalance signal: {rebalance_signal}",
                f"Monitoring {len(request.symbols)} asset class(es)",
            ],
            "regime": "NEUTRAL",
            "confidence": 0.5,
            "sentiment": sentiment,
            "source": "local_fallback",
        },
    )


def _extract_current_allocation(portfolio_req: dict) -> str:
    """Extract current allocation percentages from the portfolio request."""
    try:
        snapshot = portfolio_req.get("portfolio_snapshot", {})
        holdings = snapshot.get("holdings", [])
        total = float(snapshot.get("total_value", 0))
        if total <= 0:
            return "unknown"
        parts = []
        for h in holdings:
            pct = round(float(h.get("market_value", 0)) / total * 100, 1)
            parts.append(f"{h.get('asset_class', h.get('symbol', '?'))}: {pct}%")
        cash = float(snapshot.get("cash", 0))
        if cash > 0:
            parts.append(f"cash: {round(cash / total * 100, 1)}%")
        return ", ".join(parts) if parts else "unknown"
    except Exception:
        return "unknown"


def _extract_rebalance_signal(portfolio_req: dict) -> str:
    """Extract rebalance signal if present in the request."""
    try:
        return portfolio_req.get("rebalance_signal", "UNKNOWN")
    except Exception:
        return "UNKNOWN"


async def _run_llm_research(
    symbols: list[str],
    current_allocation: str,
    rebalance_signal: str,
) -> dict[str, Any] | None:
    """Call Bedrock for LLM-enhanced market research if feature flag is enabled."""
    llm_enabled = os.getenv("FEATURE_RESEARCH_AGENT_LLM_ENABLED", "false").lower() == "true"
    if not llm_enabled:
        return None

    try:
        from app.adapters.bedrock import BedrockModelAdapter
        from app.core.config import get_llm_config

        llm_config = get_llm_config()
        bedrock = BedrockModelAdapter()

        symbol_list = ", ".join(symbols) if symbols else "equity, fixed income, cash"

        system_prompt = (
            "You are a portfolio research analyst. Provide concise, factual market analysis "
            "for portfolio rebalancing decisions. Respond only with valid JSON."
        )

        user_prompt = f"""Analyze the current market environment for a portfolio rebalancing decision.

Portfolio asset classes: {symbol_list}
Current allocation: {current_allocation}
Rebalance signal: {rebalance_signal}

Provide a JSON response with exactly these fields:
{{
  "market_context": "2-3 sentence summary of current market conditions relevant to this allocation",
  "key_insights": ["insight 1", "insight 2", "insight 3"],
  "regime": "BULL|BEAR|NEUTRAL|VOLATILE",
  "confidence": 0.0-1.0
}}

Be specific to the asset classes mentioned. Keep insights actionable and relevant to the rebalancing decision."""

        response = await bedrock.invoke(
            model_id=llm_config.research_agent_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.4,
            max_tokens=600,
        )

        result = json.loads(response.content)

        # Validate required fields
        if not all(k in result for k in ["market_context", "key_insights", "regime", "confidence"]):
            logger.warning("LLM research response missing required fields, using fallback")
            return None

        # Validate regime value
        if result["regime"] not in ["BULL", "BEAR", "NEUTRAL", "VOLATILE"]:
            result["regime"] = "NEUTRAL"

        logger.info(f"LLM research completed: regime={result['regime']}, confidence={result['confidence']}")
        return result

    except Exception as e:
        logger.error(f"LLM research failed: {e}", exc_info=True)
        return None


async def _call_sentiment_mcp(symbols: list[str]) -> dict[str, Any]:
    mcp_url = os.getenv("SENTIMENT_MCP_URL", "http://localhost:8201/mcp")
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": "remote-research-sentiment",
                    "method": "analyze_symbol_news_sentiment",
                    "params": {"symbol": symbols[0] if symbols else "EQUITY"},
                },
            )
            response.raise_for_status()
            return response.json().get("result", {})
    except httpx.HTTPError:
        return {
            "sentiment": "NEUTRAL",
            "summary": "MCP sentiment server unavailable; used neutral fallback.",
        }
