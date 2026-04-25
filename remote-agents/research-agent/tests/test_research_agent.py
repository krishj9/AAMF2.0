from fastapi.testclient import TestClient

from app.main import app


def test_research_agent_a2a_response() -> None:
    client = TestClient(app)
    response = client.post(
        "/a2a/research",
        json={"task": "portfolio_research", "request_id": "req_test", "symbols": ["EQUITY"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["protocol"] == "A2A"
    assert body["payload"]["source"] == "remote_a2a_research_agent"
