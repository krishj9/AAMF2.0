from app.adapters.memory import LocalMemoryAdapter
from app.agents.base import completed_stage
from app.contracts.analysis import AgentStageResult
from app.contracts.workflow import PortfolioRebalanceRequest


class MemoryPersonalizationAgent:
    name = "Memory / Personalization Agent"

    def __init__(self, memory_adapter: LocalMemoryAdapter | None = None) -> None:
        self.memory_adapter = memory_adapter or LocalMemoryAdapter()

    async def run(self, request: PortfolioRebalanceRequest) -> tuple[AgentStageResult, dict]:
        memories = await self.memory_adapter.retrieve(request.client_profile.client_id)
        payload = {"items": [memory.__dict__ for memory in memories], "conflicts": []}
        return completed_stage(self.name, f"Retrieved {len(memories)} memory item(s)."), payload
