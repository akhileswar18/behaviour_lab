from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad


client = TestClient(app)


def setup_module() -> None:
    init_db()
    seed_sample_social_triad()


def test_health_contract() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert "status" in resp.json()


def test_scenarios_contract() -> None:
    list_resp = client.get("/scenarios")
    assert list_resp.status_code == 200
    assert isinstance(list_resp.json(), list)

    create_resp = client.post("/scenarios", json={"name": "contract-scenario", "description": "test"})
    assert create_resp.status_code == 201
    body = create_resp.json()
    assert "id" in body and "name" in body and "status" in body


def test_scenario_children_contract() -> None:
    scenarios = client.get("/scenarios").json()
    scenario_id = scenarios[0]["id"]

    agents = client.get(f"/scenarios/{scenario_id}/agents")
    timeline = client.get(f"/scenarios/{scenario_id}/timeline")
    relationships = client.get(f"/scenarios/{scenario_id}/relationships")
    run = client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1})

    assert agents.status_code == 200
    assert timeline.status_code == 200
    assert relationships.status_code == 200
    assert run.status_code == 200
