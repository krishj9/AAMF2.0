from app.agents.base import blocked_stage, completed_stage
from app.contracts.analysis import (
    AgentStageResult,
    DriftItem,
    PolicyVerdictStatus,
    RiskPolicyResponse,
)
from app.contracts.domain import PortfolioSnapshot, RiskProfile
from app.services.policy import evaluate_policy


class RiskComplianceAgent:
    name = "Risk & Compliance Agent"

    async def run(
        self,
        snapshot: PortfolioSnapshot,
        drift: list[DriftItem],
        risk_profile: RiskProfile | None,
    ) -> tuple[AgentStageResult, RiskPolicyResponse]:
        result = evaluate_policy(snapshot, drift, risk_profile)
        if result.verdict == PolicyVerdictStatus.NON_COMPLIANT:
            stage = blocked_stage(self.name, "Policy violation blocks trade proposal approval.")
        else:
            stage = completed_stage(self.name, f"Policy verdict: {result.verdict}.")
        return stage, result
