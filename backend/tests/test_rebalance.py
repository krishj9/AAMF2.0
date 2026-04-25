from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.routes.rebalance import get_workflow_store
from app.main import app
from app.persistence.memory_store import InMemoryWorkflowStore


def build_test_client() -> TestClient:
    store = InMemoryWorkflowStore()
    app.dependency_overrides[get_workflow_store] = lambda: store
    return TestClient(app)


def request_payload(max_single_position_pct: str = "85") -> dict:
    as_of = datetime.now(UTC).isoformat()
    return {
        "actor": {
            "actor_id": "owner",
            "display_name": "Owner",
            "role": "OWNER",
            "auth_provider": "local",
            "is_owner": True,
        },
        "client_profile": {
            "client_id": "client_demo",
            "display_label": "Demo Investor",
            "risk_profile_id": "risk_balanced",
            "synthetic": True,
        },
        "account_profile": {
            "account_id": "acct_demo",
            "client_id": "client_demo",
            "account_type": "BROKERAGE",
            "base_currency": "USD",
            "taxable": True,
        },
        "portfolio_snapshot": {
            "snapshot_id": "snap_demo",
            "account_id": "acct_demo",
            "as_of": as_of,
            "holdings": [
                {
                    "instrument_id": "inst_equity",
                    "symbol": "EQUITY",
                    "asset_class": "equity",
                    "quantity": "1",
                    "market_price": "7000",
                    "market_value": "7000",
                    "as_of": as_of,
                },
                {
                    "instrument_id": "inst_fixed_income",
                    "symbol": "BONDS",
                    "asset_class": "fixed_income",
                    "quantity": "1",
                    "market_price": "2000",
                    "market_value": "2000",
                    "as_of": as_of,
                },
            ],
            "cash": "1000",
            "total_value": "10000",
        },
        "allocation_target": {
            "target_id": "target_demo",
            "account_id": "acct_demo",
            "asset_class_targets": {"equity": "60", "fixed_income": "30", "cash": "10"},
            "tolerance_bands": {"equity": "5", "fixed_income": "5", "cash": "5"},
        },
        "risk_profile": {
            "risk_profile_id": "risk_balanced",
            "risk_level": "balanced",
            "max_single_position_pct": max_single_position_pct,
            "max_sector_pct": "60",
            "allowed_asset_classes": ["equity", "fixed_income", "cash"],
        },
    }


def test_rebalance_returns_recommendation() -> None:
    client = build_test_client()
    response = client.post("/rebalance", json=request_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["workflow_state"] == "NORMAL"
    assert body["recommendation_package"]["approval_eligibility"] is True
    assert body["approval_artifact"]["approval_status"] == "PENDING"
    stages = body["recommendation_package"]["agent_stages"]
    assert len(stages) == 7
    assert {stage["agent_name"] for stage in stages} >= {
        "Research Agent",
        "Sentiment Analysis Agent",
    }
    assert all("protocol" in stage for stage in stages)
    assert all("execution_location" in stage for stage in stages)


def test_rebalance_blocks_concentration_failure() -> None:
    client = build_test_client()
    response = client.post("/rebalance", json=request_payload(max_single_position_pct="50"))

    assert response.status_code == 200
    body = response.json()
    assert body["workflow_state"] == "BLOCKED"
    assert body["recommendation_package"]["risk_policy"]["verdict"] == "NON_COMPLIANT"


def test_approval_action_updates_artifact() -> None:
    client = build_test_client()
    response = client.post("/rebalance", json=request_payload())
    body = response.json()
    approval = body["approval_artifact"]

    action_response = client.post(
        f"/approvals/{approval['approval_id']}/actions",
        json={
            "action": "APPROVE",
            "actor_id": "owner",
            "expected_recommendation_hash": approval["recommendation_hash"],
        },
    )

    assert action_response.status_code == 200
    assert action_response.json()["next_status"] == "APPROVED"
