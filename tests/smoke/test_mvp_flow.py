from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad


client = TestClient(app)


def test_mvp_seed_run_inspect_flow() -> None:
    init_db()
    seed_sample_social_triad()

    scenarios = client.get("/scenarios").json()
    assert scenarios, "expected seeded scenarios"
    scenario_id = scenarios[0]["id"]

    run = client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 3})
    assert run.status_code == 200
    assert run.json()["end_tick"] >= 3

    timeline = client.get(f"/scenarios/{scenario_id}/timeline")
    agents = client.get(f"/scenarios/{scenario_id}/agents")
    relationships = client.get(f"/scenarios/{scenario_id}/relationships")

    assert timeline.status_code == 200
    assert agents.status_code == 200
    assert relationships.status_code == 200
    assert len(agents.json()) >= 3
