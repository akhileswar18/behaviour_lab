from fastapi.testclient import TestClient


def test_goal_intention_persistence_and_transitions(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 4})

    goals = phase3_seeded_client.get(f"/scenarios/{scenario_id}/goals").json()
    intentions = phase3_seeded_client.get(f"/scenarios/{scenario_id}/intentions").json()

    assert goals
    assert intentions
    assert any(goal["status"] in {"active", "completed", "deferred", "interrupted"} for goal in goals)
    assert any(intent["status"] in {"active", "completed", "deferred", "interrupted"} for intent in intentions)
