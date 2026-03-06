from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_shape():
    client = TestClient(app)
    res = client.get("/metrics")
    assert res.status_code == 200
    payload = res.json()
    assert "strategies" in payload
    assert "paper" in payload
