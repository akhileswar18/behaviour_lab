from collections import defaultdict

from fastapi.testclient import TestClient

from app.api.main import app
from app.persistence.init_db import init_db
from app.persistence.seed import seed_sample_social_triad


def test_persona_deterministic_action_divergence() -> None:
    init_db()
    seed_sample_social_triad()
    client = TestClient(app)

    scenario_id = client.get("/scenarios").json()[0]["id"]
    agents = client.get(f"/scenarios/{scenario_id}/agents").json()
    id_to_name = {row["id"]: row["name"] for row in agents}

    run_response = client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1})
    assert run_response.status_code == 200

    timeline = client.get(
        f"/scenarios/{scenario_id}/timeline",
        params={"event_type": "decision", "tick_from": 1, "tick_to": 1},
    ).json()
    assert timeline

    by_agent = defaultdict(list)
    for row in timeline:
        actor = row["actor_agent_id"]
        if actor:
            by_agent[actor].append(row["payload"]["action"])

    distinct_actions = {actions[0] for actions in by_agent.values() if actions}
    assert len(distinct_actions) >= 2
    assert len(by_agent) >= 3
    assert set(by_agent.keys()).issubset(set(id_to_name.keys()))
