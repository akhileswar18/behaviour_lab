from fastapi.testclient import TestClient


def test_world_analytics_matches_zone_and_resource_views(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 8})

    world = phase3_seeded_client.get(f"/scenarios/{scenario_id}/analytics/world").json()
    zones = phase3_seeded_client.get(f"/scenarios/{scenario_id}/zones").json()
    resources = phase3_seeded_client.get(f"/scenarios/{scenario_id}/resources").json()

    assert len(world["zone_occupancy"]) == len(zones)
    assert len(world["resource_distribution"]) == len(resources)
    assert world["world_state"]["zone_count"] == len(zones)


def test_world_analytics_exposes_macro_metrics(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 8})

    world = phase3_seeded_client.get(f"/scenarios/{scenario_id}/analytics/world").json()

    assert {"average_trust", "goal_completion_rate", "movement_frequency", "resource_scarcity"}.issubset(world["metrics"].keys())
