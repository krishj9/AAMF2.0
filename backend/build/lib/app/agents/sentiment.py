import httpx

from app.agents.base import completed_stage
from app.contracts.analysis import AgentStageResult
from app.contracts.workflow import PortfolioRebalanceRequest
from app.core.config import Settings, get_settings


class SentimentAnalysisAgent:
    name = "Sentiment Analysis Agent"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def run(self, request: PortfolioRebalanceRequest) -> tuple[AgentStageResult, dict]:
        symbols = [holding.symbol for holding in request.portfolio_snapshot.holdings]
        if self.settings.sentiment_mcp_enabled:
            try:
                return await self._run_mcp(symbols)
            except (httpx.HTTPError, ValueError):
                pass
        return self._run_local(symbols)

    async def _run_mcp(self, symbols: list[str]) -> tuple[AgentStageResult, dict]:
        async with httpx.AsyncClient(timeout=self.settings.remote_agent_timeout_seconds) as client:
            response = await client.post(
                self.settings.sentiment_mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": "sentiment-analysis",
                    "method": "tools/call",
                    "params": {
                        "name": "analyze_symbol_news_sentiment",
                        "arguments": {"symbols": symbols},
                    },
                },
            )
            response.raise_for_status()
            body = response.json()
        result = body.get("result", {})
        stage = completed_stage(
            self.name,
            result.get("summary", "MCP sentiment tool returned sentiment signals."),
            protocol="MCP",
            execution_location="mcp_server",
        )
        return stage, result

    def _run_local(self, symbols: list[str]) -> tuple[AgentStageResult, dict]:
        payload = {
            "symbols": symbols,
            "sentiment": "NEUTRAL",
            "summary": "No live news feed is configured yet; sentiment defaults to neutral.",
        }
        return (
            completed_stage(
                self.name,
                "Generated neutral fallback sentiment.",
                protocol="LOCAL",
                execution_location="in_process_fallback",
            ),
            payload,
        )
