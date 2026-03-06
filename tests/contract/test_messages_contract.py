from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad


client = TestClient(app)


def test_messages_contract_fields() -> None:
    init_db()
    seed_sample_social_triad()
    scenario_id = client.get("/scenarios").json()[0]["id"]

    run_resp = client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1})
    assert run_resp.status_code == 200

    response = client.get(f"/scenarios/{scenario_id}/messages")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload, "Expected seeded or runtime messages"

    first = payload[0]
    required = {
        "id",
        "scenario_id",
        "tick_number",
        "sender_agent_id",
        "receiver_agent_id",
        "target_mode",
        "content",
        "intent",
        "emotional_tone",
        "intent_tags",
        "created_at",
    }
    assert required.issubset(set(first.keys()))
