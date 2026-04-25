import hashlib

from app.agents.base import completed_stage
from app.contracts.analysis import AgentStageResult, ApprovalArtifact, RecommendationPackage
from app.contracts.common import CorrelationMetadata, new_id
from app.contracts.workflow import PortfolioRebalanceRequest


class HumanApprovalWorkflowAgent:
    name = "Human Approval Workflow Agent"

    async def run(
        self,
        correlation: CorrelationMetadata,
        recommendation: RecommendationPackage,
        request: PortfolioRebalanceRequest,
    ) -> tuple[AgentStageResult, ApprovalArtifact]:
        stage = completed_stage(self.name, "Created pending human approval artifact.")
        recommendation.agent_stages.append(stage)
        approval = ApprovalArtifact(
            approval_id=new_id("apr"),
            correlation=correlation,
            recommendation_hash=self._hash_recommendation(recommendation),
            recommendation=recommendation,
            client_profile=request.client_profile,
            account_profile=request.account_profile,
            original_portfolio_snapshot=request.portfolio_snapshot,
            allocation_target=request.allocation_target,
            risk_profile=request.risk_profile,
        )
        return stage, approval

    def _hash_recommendation(self, recommendation: RecommendationPackage) -> str:
        payload = recommendation.model_dump_json()
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
