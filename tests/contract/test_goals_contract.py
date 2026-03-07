from fastapi.testclient import TestClient


def test_goals_and_intentions_contract(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]

    goals = phase3_seeded_client.get(f"/scenarios/{scenario_id}/goals")
    intentions = phase3_seeded_client.get(f"/scenarios/{scenario_id}/intentions")

    assert goals.status_code == 200
    assert intentions.status_code == 200
    goal_row = goals.json()[0]
    intention_row = intentions.json()[0]
    assert {"id", "goal_type", "priority", "status", "target", "source"}.issubset(goal_row.keys())
    assert {"id", "current_action_type", "status", "rationale"}.issubset(intention_row.keys())
