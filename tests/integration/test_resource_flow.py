from fastapi.testclient import TestClient


def test_resource_acquire_consume_and_shortage(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 8})

    resources = phase3_seeded_client.get(f"/scenarios/{scenario_id}/resources").json()
    timeline = phase3_seeded_client.get(f"/scenarios/{scenario_id}/timeline").json()

    assert resources
    assert any(event["event_type"] in {"acquire", "consume", "resource_shortage"} for event in timeline)
