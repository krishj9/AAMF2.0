from decimal import Decimal

from app.agents.base import completed_stage
from app.contracts.analysis import AgentStageResult, DriftItem
from app.contracts.workflow import PortfolioRebalanceRequest
from app.services.portfolio import calculate_asset_allocation, calculate_drift


class PortfolioRebalancingAgent:
    name = "Portfolio Rebalancing Agent"

    async def run(
        self, request: PortfolioRebalanceRequest
    ) -> tuple[AgentStageResult, dict[str, dict[str, Decimal] | list[DriftItem]]]:
        current_allocation = calculate_asset_allocation(request.portfolio_snapshot)
        drift = calculate_drift(request.portfolio_snapshot, request.allocation_target)
        out_of_tolerance = [item for item in drift if not item.within_tolerance]
        return (
            completed_stage(
                self.name,
                (
                    "Calculated allocation drift with "
                    f"{len(out_of_tolerance)} target(s) outside tolerance."
                ),
            ),
            {
                "current_allocation": current_allocation,
                "target_allocation": request.allocation_target.asset_class_targets,
                "drift": drift,
            },
        )
