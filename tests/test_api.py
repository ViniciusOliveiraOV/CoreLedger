import json
from starlette.testclient import TestClient

from api.standalone_api import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data


def test_get_dashboard():
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "kpis" in data
    assert "charts" in data


def test_simulate_transaction():
    r = client.post("/api/simulate/random-transaction")
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True


def test_websocket_initial_update():
    with client.websocket_connect("/ws") as websocket:
        message = websocket.receive_text()
        data = json.loads(message)
        assert data.get("type") == "dashboard_update"
        assert "data" in data
