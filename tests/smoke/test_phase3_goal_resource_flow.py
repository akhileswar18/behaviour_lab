from fastapi.testclient import TestClient



def test_phase3_goal_resource_flow(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    run = phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 8})
    assert run.status_code == 200

    agents = phase3_seeded_client.get(f"/scenarios/{scenario_id}/agents").json()
    goals = phase3_seeded_client.get(f"/scenarios/{scenario_id}/goals").json()
    zones = phase3_seeded_client.get(f"/scenarios/{scenario_id}/zones").json()
    resources = phase3_seeded_client.get(f"/scenarios/{scenario_id}/resources").json()
    timeline = phase3_seeded_client.get(f"/scenarios/{scenario_id}/timeline").json()

    assert agents and goals and zones and resources
    assert any(agent.get("active_goal") for agent in agents)
    assert any(event["event_type"] == "plan_change" for event in timeline)
    assert any(event["event_type"] in {"move", "acquire", "consume", "resource_shortage"} for event in timeline)
