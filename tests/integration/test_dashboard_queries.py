from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad


client = TestClient(app)


def test_dashboard_queries_timeline_and_messages() -> None:
    init_db()
    seed_sample_social_triad()
    scenario_id = client.get("/scenarios").json()[0]["id"]

    client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1})

    timeline = client.get(f"/scenarios/{scenario_id}/timeline", params={"tick_from": 1, "tick_to": 1})
    messages = client.get(f"/scenarios/{scenario_id}/messages")

    assert timeline.status_code == 200
    assert messages.status_code == 200
    assert isinstance(timeline.json(), list)
    assert isinstance(messages.json(), list)
