from fastapi.testclient import TestClient

from app.api.routes.portfolios import get_workflow_store
from app.main import app
from app.persistence.memory_store import InMemoryWorkflowStore


def test_list_portfolios_returns_seeded_clients() -> None:
    app.dependency_overrides[get_workflow_store] = lambda: InMemoryWorkflowStore()
    client = TestClient(app)

    response = client.get("/portfolios")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 2
    assert {portfolio["account_profile"]["account_id"] for portfolio in body} >= {
        "acct_demo",
        "acct_income",
    }
