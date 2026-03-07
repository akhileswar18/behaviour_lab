from fastapi.testclient import TestClient



def test_need_driven_planning_changes_actions(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 6})

    timeline = phase3_seeded_client.get(f"/scenarios/{scenario_id}/timeline").json()
    assert any(event["event_type"] == "need_threshold" for event in timeline)
    assert any(event["event_type"] in {"move", "acquire", "consume"} for event in timeline)
