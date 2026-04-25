from fastapi.testclient import TestClient

from app.api.routes.market import get_workflow_store
from app.main import app
from app.persistence.memory_store import InMemoryWorkflowStore


def test_market_stream_emits_sse_event() -> None:
    app.dependency_overrides[get_workflow_store] = lambda: InMemoryWorkflowStore()
    client = TestClient(app)

    with client.stream("GET", "/market/stream?limit=1&interval_ms=100") as response:
        payload = response.read().decode("utf-8")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "data:" in payload
    assert "equity_change_pct" in payload
    assert "REBALANCE_NEEDED" in payload or "WATCH" in payload or "NO_ACTION" in payload
