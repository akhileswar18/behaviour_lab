from fastapi.testclient import TestClient


def test_planning_variant_compare_supports_world_and_needs_overrides(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    payload = {
        "ticks": 5,
        "variant_name": "hungry-ben",
        "planning_overrides": {"Ben": {"hunger": 0.95}},
        "world_overrides": {"Storage": {"food": 0}},
    }
    response = phase3_seeded_client.post(f"/scenarios/{scenario_id}/compare-rerun", json=payload)
    assert response.status_code == 200
    body = response.json()
    differences = body["comparison"]["differences"]
    assert "completed_goal_delta" in differences
    assert "move_event_delta" in differences
    assert "resource_event_delta" in differences
