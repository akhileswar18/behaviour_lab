from fastapi.testclient import TestClient



def test_goal_resource_variant_diff(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    payload = {
        "ticks": 5,
        "variant_name": "resource-scarce",
        "planning_overrides": {"Ben": {"hunger": 0.95}},
        "world_overrides": {"Storage": {"food": 0}},
    }
    response = phase3_seeded_client.post(f"/scenarios/{scenario_id}/compare-rerun", json=payload)
    differences = response.json()["comparison"]["differences"]
    assert response.status_code == 200
    assert sum(int(value != 0) for value in differences.values()) >= 1
