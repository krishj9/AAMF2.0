from app.agents.base import blocked_stage, completed_stage
from app.contracts.analysis import AgentStageResult, ExecutionProposalResponse, RiskPolicyResponse
from app.contracts.domain import PortfolioSnapshot
from app.services.proposal import generate_execution_proposal


class TradeExecutionProposalAgent:
    name = "Trade Execution Proposal Agent"

    async def run(
        self, snapshot: PortfolioSnapshot, risk_policy: RiskPolicyResponse
    ) -> tuple[AgentStageResult, ExecutionProposalResponse]:
        proposal = generate_execution_proposal(snapshot, risk_policy)
        if proposal.proposal_status == "BLOCKED":
            stage = blocked_stage(self.name, "Trade proposal skipped because policy blocked.")
            return stage, proposal
        stage = completed_stage(self.name, f"Trade proposal status: {proposal.proposal_status}.")
        return stage, proposal
