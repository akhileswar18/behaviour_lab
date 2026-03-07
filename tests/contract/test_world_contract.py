from fastapi.testclient import TestClient


def test_world_contract(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]

    zones = phase3_seeded_client.get(f"/scenarios/{scenario_id}/zones")
    resources = phase3_seeded_client.get(f"/scenarios/{scenario_id}/resources")

    assert zones.status_code == 200
    assert resources.status_code == 200
    zone_row = zones.json()[0]
    resource_row = resources.json()[0]
    assert {"id", "name", "zone_type", "occupant_ids", "resource_types"}.issubset(zone_row.keys())
    assert {"id", "zone_id", "resource_type", "quantity", "status"}.issubset(resource_row.keys())
