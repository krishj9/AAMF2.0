from app.agents.base import completed_stage
from app.contracts.analysis import AgentStageResult
from app.contracts.workflow import PortfolioRebalanceRequest


class ResearchAgent:
    name = "Research Agent"

    async def run(self, request: PortfolioRebalanceRequest) -> tuple[AgentStageResult, dict]:
        holdings = request.portfolio_snapshot.holdings
        symbols = ", ".join(holding.symbol for holding in holdings)
        payload = {
            "symbols": [holding.symbol for holding in holdings],
            "summary": f"Using request-provided market values for {symbols}.",
            "source": "request_payload",
        }
        return completed_stage(self.name, "Prepared market context from request holdings."), payload
