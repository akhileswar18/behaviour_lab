from fastapi.testclient import TestClient


def test_world_analytics_contract(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 6})

    response = phase3_seeded_client.get(f"/scenarios/{scenario_id}/analytics/world")

    assert response.status_code == 200
    payload = response.json()
    assert {
        "scenario_id",
        "current_tick",
        "world_state",
        "global_event_feed",
        "zone_occupancy",
        "resource_distribution",
        "metrics",
    }.issubset(payload.keys())
    assert {"zone_count", "agent_count", "resource_unit_count"}.issubset(payload["world_state"].keys())
