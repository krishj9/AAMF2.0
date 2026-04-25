from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.contracts import (
    ActorContext,
    OrchestrationResponse,
    PortfolioRebalanceRequest,
    SeedManifest,
    WorkflowState,
)
from app.contracts.domain import (
    AccountProfile,
    AllocationTarget,
    ClientProfile,
    PortfolioHolding,
    PortfolioSnapshot,
    RiskProfile,
)


def build_request() -> PortfolioRebalanceRequest:
    as_of = datetime.now(UTC)
    holding = PortfolioHolding(
        instrument_id="inst_vti",
        symbol="VTI",
        quantity=Decimal("10"),
        market_price=Decimal("100"),
        market_value=Decimal("1000"),
        as_of=as_of,
    )
    return PortfolioRebalanceRequest(
        actor=ActorContext(actor_id="owner", display_name="Owner"),
        client_profile=ClientProfile(
            client_id="client_demo",
            display_label="Demo Investor",
            risk_profile_id="risk_balanced",
        ),
        account_profile=AccountProfile(account_id="acct_demo", client_id="client_demo"),
        portfolio_snapshot=PortfolioSnapshot(
            snapshot_id="snap_demo",
            account_id="acct_demo",
            as_of=as_of,
            holdings=[holding],
            cash=Decimal("0"),
            total_value=Decimal("1000"),
        ),
        allocation_target=AllocationTarget(
            target_id="target_demo",
            account_id="acct_demo",
            asset_class_targets={"equity": Decimal("80"), "fixed_income": Decimal("20")},
        ),
        risk_profile=RiskProfile(
            risk_profile_id="risk_balanced",
            risk_level="balanced",
            max_single_position_pct=Decimal("25"),
            max_sector_pct=Decimal("40"),
            allowed_asset_classes=["equity", "fixed_income"],
        ),
    )


def test_portfolio_rebalance_request_contract_accepts_valid_payload() -> None:
    request = build_request()

    assert request.correlation.request_id.startswith("req_")
    assert request.version.schema_version == "1.0.0"


def test_allocation_target_requires_total_of_100() -> None:
    with pytest.raises(ValidationError):
        AllocationTarget(
            target_id="target_invalid",
            account_id="acct_demo",
            asset_class_targets={"equity": Decimal("90"), "fixed_income": Decimal("5")},
        )


def test_orchestration_response_carries_correlation_and_version() -> None:
    request = build_request()
    response = OrchestrationResponse(
        correlation=request.correlation,
        version=request.version,
        workflow_state=WorkflowState.DEGRADED,
    )

    assert response.correlation.trace_id == request.correlation.trace_id
    assert response.workflow_state == WorkflowState.DEGRADED


def test_seed_manifest_contract_accepts_example_shape() -> None:
    manifest = SeedManifest(
        manifest_version="1.0.0",
        dataset_id="personal-demo",
        dataset_version="2026-04-24",
        environment="dev",
        created_by="test",
        created_at=datetime.now(UTC),
        idempotency_key="personal-demo-dev",
        manifest_checksum_sha256="replace-with-generated-manifest-checksum",
        provenance={"source": "synthetic"},
        domains=[
            {
                "domain": "client_profiles",
                "schema_version": "1.0.0",
                "record_count": 1,
                "file": "seeds/client_profiles.jsonl",
                "checksum_sha256": "replace-with-generated-checksum",
                "load_order": 1,
            }
        ],
    )

    assert manifest.synthetic is True
    assert manifest.domains[0].domain == "client_profiles"
