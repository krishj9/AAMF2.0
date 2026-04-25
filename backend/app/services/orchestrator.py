import hashlib

from app.contracts.analysis import ApprovalArtifact, RecommendationPackage
from app.contracts.common import WorkflowState, new_id
from app.contracts.workflow import OrchestrationResponse, PortfolioRebalanceRequest
from app.persistence.memory_store import workflow_store
from app.services.policy import evaluate_policy
from app.services.portfolio import calculate_asset_allocation, calculate_drift
from app.services.proposal import generate_execution_proposal


class Orchestrator:
    async def run(self, request: PortfolioRebalanceRequest) -> OrchestrationResponse:
        workflow_store.add_audit_event(
            event_type="REQUEST_RECEIVED",
            correlation=request.correlation,
            actor_id=request.actor.actor_id,
            outcome="ACCEPTED",
        )

        current_allocation = calculate_asset_allocation(request.portfolio_snapshot)
        drift = calculate_drift(request.portfolio_snapshot, request.allocation_target)
        risk_policy = evaluate_policy(request.portfolio_snapshot, drift, request.risk_profile)
        proposal = generate_execution_proposal(request.portfolio_snapshot, risk_policy)

        workflow_state = WorkflowState.NORMAL
        approval_eligibility = proposal.proposal_status in {"READY_FOR_REVIEW", "NO_ACTION_NEEDED"}
        if proposal.proposal_status == "BLOCKED":
            workflow_state = WorkflowState.BLOCKED
            approval_eligibility = False
        elif proposal.proposal_status == "NO_ACTION_NEEDED":
            workflow_state = WorkflowState.LOW_CONFIDENCE

        recommendation = RecommendationPackage(
            summary=self._summary(proposal.proposal_status),
            current_allocation=current_allocation,
            target_allocation=request.allocation_target.asset_class_targets,
            proposed_allocation=proposal.estimated_impact or current_allocation,
            risk_policy=risk_policy,
            proposal=proposal,
            workflow_state=workflow_state,
            approval_eligibility=approval_eligibility,
            evidence=risk_policy.evidence,
        )
        approval = ApprovalArtifact(
            approval_id=new_id("apr"),
            correlation=request.correlation,
            recommendation_hash=self._hash_recommendation(recommendation),
            recommendation=recommendation,
        )
        workflow_store.save_approval(approval)
        workflow_store.add_audit_event(
            event_type="APPROVAL_ARTIFACT_CREATED",
            correlation=request.correlation,
            actor_id=request.actor.actor_id,
            outcome=approval.approval_status,
            details={"approval_id": approval.approval_id},
        )

        return OrchestrationResponse(
            correlation=request.correlation,
            version=request.version,
            workflow_state=workflow_state,
            recommendation_package=recommendation,
            approval_artifact=approval,
        )

    def _hash_recommendation(self, recommendation: RecommendationPackage) -> str:
        payload = recommendation.model_dump_json()
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _summary(self, proposal_status: str) -> str:
        if proposal_status == "BLOCKED":
            return "Recommendation is blocked by deterministic policy checks."
        if proposal_status == "NO_ACTION_NEEDED":
            return "Portfolio is already within configured allocation tolerances."
        return "Portfolio has drift outside tolerance and is ready for manual review."
