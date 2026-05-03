from typing import Any

from pydantic import Field

from app.contracts.analysis import ApprovalArtifact, RecommendationPackage
from app.contracts.common import (
    ActorContext,
    ContractModel,
    CorrelationMetadata,
    StructuredError,
    VersionMetadata,
    WorkflowState,
)
from app.contracts.domain import (
    AccountProfile,
    AllocationTarget,
    ClientProfile,
    PortfolioSnapshot,
    RiskProfile,
)


class PortfolioRebalanceRequest(ContractModel):
    correlation: CorrelationMetadata = Field(default_factory=CorrelationMetadata)
    version: VersionMetadata = Field(default_factory=VersionMetadata)
    actor: ActorContext
    client_profile: ClientProfile
    account_profile: AccountProfile
    portfolio_snapshot: PortfolioSnapshot
    allocation_target: AllocationTarget
    risk_profile: RiskProfile | None = None
    constraints: dict[str, Any] = Field(default_factory=dict)
    requested_action_context: str = "rebalance_review"


class GraphState(ContractModel):
    correlation: CorrelationMetadata
    version: VersionMetadata
    actor: ActorContext
    request: PortfolioRebalanceRequest
    research: dict[str, Any] | None = None
    memory: dict[str, Any] | None = None
    risk_policy: dict[str, Any] | None = None
    proposal: dict[str, Any] | None = None
    guardrail_result: dict[str, Any] | None = None
    quality: dict[str, Any] = Field(default_factory=dict)
    errors: list[StructuredError] = Field(default_factory=list)


class OrchestrationResponse(ContractModel):
    correlation: CorrelationMetadata
    version: VersionMetadata
    workflow_state: WorkflowState
    recommendation_package: RecommendationPackage | None = None
    approval_artifact: ApprovalArtifact | None = None
    structured_error: StructuredError | None = None
    provider_trace_url: str | None = None
    research_output: dict[str, Any] | None = None
    sentiment_output: dict[str, Any] | None = None
