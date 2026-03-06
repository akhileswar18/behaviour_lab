from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad


client = TestClient(app)


def test_tick_progression_generates_decision_events() -> None:
    init_db()
    seed_sample_social_triad()

    scenario_id = client.get("/scenarios").json()[0]["id"]
    run_response = client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 10})
    assert run_response.status_code == 200

    timeline = client.get(f"/scenarios/{scenario_id}/timeline").json()
    decision_events = [e for e in timeline if e["event_type"] == "decision"]
    assert len(decision_events) >= 10
