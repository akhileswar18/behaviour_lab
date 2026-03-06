from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad


client = TestClient(app)


def test_simulation_run_endpoint_persists_ticks() -> None:
    init_db()
    seed_sample_social_triad()

    scenarios = client.get("/scenarios").json()
    scenario_id = scenarios[0]["id"]

    response = client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["end_tick"] >= 2
    assert len(body["tick_results"]) == 2
