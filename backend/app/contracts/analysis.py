from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import Field

from app.contracts.common import ContractModel, CorrelationMetadata, WorkflowState


class PolicyVerdictStatus(StrEnum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNRESOLVED = "UNRESOLVED"


class TradeAction(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class DriftItem(ContractModel):
    key: str
    current_pct: Decimal
    target_pct: Decimal
    drift_pct: Decimal
    tolerance_pct: Decimal
    within_tolerance: bool


class RiskPolicyResponse(ContractModel):
    verdict: PolicyVerdictStatus
    drift: list[DriftItem]
    rule_results: list[dict[str, str | bool]] = Field(default_factory=list)
    evidence: list[dict[str, str]] = Field(default_factory=list)
    confidence: dict[str, str | Decimal] = Field(default_factory=dict)


class TradeProposal(ContractModel):
    trade_id: str
    symbol: str
    action: TradeAction
    estimated_value: Decimal
    rationale: str
    evidence_refs: list[str] = Field(default_factory=list)


class ExecutionProposalResponse(ContractModel):
    proposal_status: str
    trades: list[TradeProposal] = Field(default_factory=list)
    estimated_impact: dict[str, Decimal] = Field(default_factory=dict)
    estimated_cost: Decimal = Decimal("0")
    tax_notes: list[str] = Field(default_factory=list)
    confidence: dict[str, str | Decimal] = Field(default_factory=dict)


class RecommendationPackage(ContractModel):
    summary: str
    current_allocation: dict[str, Decimal]
    target_allocation: dict[str, Decimal]
    proposed_allocation: dict[str, Decimal]
    risk_policy: RiskPolicyResponse
    proposal: ExecutionProposalResponse
    workflow_state: WorkflowState
    approval_eligibility: bool
    evidence: list[dict[str, str]] = Field(default_factory=list)


class ApprovalArtifact(ContractModel):
    approval_id: str
    correlation: CorrelationMetadata
    recommendation_hash: str
    recommendation: RecommendationPackage
    approval_status: str = "PENDING"
    approved_by: str | None = None
    approved_at: datetime | None = None
    rejection_note: str | None = None
    override_note: str | None = None


class AuditEvent(ContractModel):
    event_id: str
    event_type: str
    correlation: CorrelationMetadata
    actor_id: str | None = None
    outcome: str
    details: dict[str, str] = Field(default_factory=dict)
    created_at: datetime
