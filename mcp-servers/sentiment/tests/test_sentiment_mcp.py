from fastapi.testclient import TestClient

from app.main import app


def test_sentiment_mcp_tool_call() -> None:
    client = TestClient(app)
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": "test",
            "method": "tools/call",
            "params": {
                "name": "analyze_symbol_news_sentiment",
                "arguments": {"symbols": ["EQUITY", "BONDS"]},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["sentiment"] == "CAUTIOUS"
