from decimal import Decimal

from app.contracts.analysis import (
    DriftItem,
    ExecutionProposalResponse,
    PolicyVerdictStatus,
    RiskPolicyResponse,
    TradeAction,
    TradeProposal,
)
from app.contracts.common import new_id
from app.contracts.domain import PortfolioSnapshot


def generate_execution_proposal(
    snapshot: PortfolioSnapshot,
    risk_policy: RiskPolicyResponse,
) -> ExecutionProposalResponse:
    if risk_policy.verdict != PolicyVerdictStatus.COMPLIANT:
        return ExecutionProposalResponse(
            proposal_status="BLOCKED",
            confidence={"score": Decimal("0.0"), "label": "blocked"},
        )

    trades = [
        _trade_for_drift(snapshot, item)
        for item in risk_policy.drift
        if not item.within_tolerance
    ]
    return ExecutionProposalResponse(
        proposal_status="READY_FOR_REVIEW" if trades else "NO_ACTION_NEEDED",
        trades=[trade for trade in trades if trade is not None],
        estimated_impact={item.key: item.target_pct for item in risk_policy.drift},
        confidence={"score": Decimal("0.75"), "label": "medium"},
    )


def _trade_for_drift(snapshot: PortfolioSnapshot, item: DriftItem) -> TradeProposal | None:
    if item.target_pct == Decimal("0") and item.current_pct == Decimal("0"):
        return None

    estimated_value = abs(item.drift_pct / Decimal("100") * snapshot.total_value)
    action = TradeAction.SELL if item.drift_pct > 0 else TradeAction.BUY
    return TradeProposal(
        trade_id=new_id("trd"),
        symbol=item.key.upper(),
        action=action,
        estimated_value=estimated_value.quantize(Decimal("0.01")),
        rationale=(
            f"{action} {item.key} exposure to move from "
            f"{item.current_pct}% toward {item.target_pct}%."
        ),
        evidence_refs=["policy_drift_check"],
    )
