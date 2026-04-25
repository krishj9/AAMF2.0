from app.agents.base import completed_stage
from app.contracts.analysis import AgentStageResult
from app.contracts.workflow import PortfolioRebalanceRequest


class SentimentAnalysisAgent:
    name = "Sentiment Analysis Agent"

    async def run(self, request: PortfolioRebalanceRequest) -> tuple[AgentStageResult, dict]:
        symbols = [holding.symbol for holding in request.portfolio_snapshot.holdings]
        payload = {
            "symbols": symbols,
            "sentiment": "NEUTRAL",
            "summary": "No live news feed is configured yet; sentiment defaults to neutral.",
        }
        return completed_stage(self.name, "Generated neutral placeholder sentiment."), payload
