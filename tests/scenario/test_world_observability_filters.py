from fastapi.testclient import TestClient


def test_world_observability_honors_zone_and_event_filters(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 8})

    zones = phase3_seeded_client.get(f"/scenarios/{scenario_id}/zones").json()
    zone_id = zones[0]["id"]

    world = phase3_seeded_client.get(
        f"/scenarios/{scenario_id}/analytics/world",
        params={"zone_id": zone_id, "event_type": "move"},
    ).json()

    assert all(row["zone_id"] == zone_id for row in world["zone_occupancy"])
    assert all(event["event_type"] == "move" for event in world["global_event_feed"])
