from decimal import Decimal

from app.contracts.analysis import DriftItem, PolicyVerdictStatus, RiskPolicyResponse
from app.contracts.domain import PortfolioSnapshot, RiskProfile


def evaluate_policy(
    snapshot: PortfolioSnapshot,
    drift: list[DriftItem],
    risk_profile: RiskProfile | None,
) -> RiskPolicyResponse:
    rule_results: list[dict[str, str | bool]] = []

    out_of_tolerance = [item for item in drift if not item.within_tolerance]
    rule_results.append(
        {
            "rule_id": "allocation_tolerance",
            "passed": not out_of_tolerance,
            "message": "All allocation targets are within tolerance."
            if not out_of_tolerance
            else "One or more allocation targets are outside tolerance.",
        }
    )

    if risk_profile is None:
        return RiskPolicyResponse(
            verdict=PolicyVerdictStatus.UNRESOLVED,
            drift=drift,
            rule_results=rule_results
            + [
                {
                    "rule_id": "risk_profile_present",
                    "passed": False,
                    "message": "Risk profile is required for approval eligibility.",
                }
            ],
            confidence={"score": Decimal("0.60"), "label": "medium"},
        )

    largest_position_pct = max(
        (holding.market_value / snapshot.total_value) * Decimal("100")
        for holding in snapshot.holdings
    )
    concentration_passed = largest_position_pct <= risk_profile.max_single_position_pct
    rule_results.append(
        {
            "rule_id": "single_position_concentration",
            "passed": concentration_passed,
            "message": "Largest position is within configured concentration limit."
            if concentration_passed
            else "Largest position exceeds configured concentration limit.",
        }
    )

    verdict = (
        PolicyVerdictStatus.NON_COMPLIANT
        if not concentration_passed
        else PolicyVerdictStatus.COMPLIANT
    )

    return RiskPolicyResponse(
        verdict=verdict,
        drift=drift,
        rule_results=rule_results,
        evidence=[
            {
                "evidence_id": "policy_drift_check",
                "summary": "Deterministic allocation drift and concentration checks.",
            }
        ],
        confidence={"score": Decimal("0.90"), "label": "high"},
    )
