from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_scenario


client = TestClient(app)


def test_phase2_social_flow_smoke() -> None:
    init_db()
    seed_scenario("sample_social_tension")

    scenarios = client.get("/scenarios")
    assert scenarios.status_code == 200
    scenario_id = scenarios.json()[0]["id"]

    run_response = client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 4})
    assert run_response.status_code == 200

    messages = client.get(f"/scenarios/{scenario_id}/messages")
    relationships = client.get(f"/scenarios/{scenario_id}/relationships")
    world_events = client.get(
        f"/scenarios/{scenario_id}/timeline",
        params={"event_type": "world_event"},
    )
    decision_events = client.get(
        f"/scenarios/{scenario_id}/timeline",
        params={"event_type": "decision"},
    )
    relationship_events = client.get(
        f"/scenarios/{scenario_id}/timeline",
        params={"event_type": "relationship_update"},
    )

    assert messages.status_code == 200
    assert relationships.status_code == 200
    assert world_events.status_code == 200
    assert decision_events.status_code == 200
    assert relationship_events.status_code == 200

    message_rows = messages.json()
    relationship_rows = relationships.json()
    world_event_rows = world_events.json()
    decision_rows = decision_events.json()
    relationship_event_rows = relationship_events.json()

    assert message_rows, "expected persisted social messages"
    assert any(row["intent"] for row in message_rows)
    assert relationship_rows, "expected persisted relationships"
    assert any(row["last_updated_tick"] >= 1 for row in relationship_rows)
    assert world_event_rows, "expected seeded world events to be consumed"
    assert decision_rows, "expected decision events"
    assert relationship_event_rows, "expected relationship update events"
    assert any("decision_id" in row["payload"] for row in relationship_event_rows)
