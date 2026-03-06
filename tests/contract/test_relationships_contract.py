from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad


client = TestClient(app)


def test_relationships_contract_fields() -> None:
    init_db()
    seed_sample_social_triad()
    scenario_id = client.get("/scenarios").json()[0]["id"]
    client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1})

    response = client.get(f"/scenarios/{scenario_id}/relationships")
    assert response.status_code == 200
    payload = response.json()
    assert payload

    first = payload[0]
    required = {
        "source_agent_id",
        "target_agent_id",
        "trust",
        "affinity",
        "stance",
        "influence",
        "last_updated_tick",
        "last_interaction_at",
        "updated_at",
    }
    assert required.issubset(set(first.keys()))
