from fastapi.testclient import TestClient

from src.cred_support_agent.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_endpoint():
    response = client.post("/ask", json={"query": "What are the eligibility rules for home loans?", "record_id": "CL-0001"})
    assert response.status_code == 200
    payload = response.json()
    assert "answer" in payload
    assert payload["status"] in {"ok", "refused"}
