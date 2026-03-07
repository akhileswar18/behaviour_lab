from fastapi.testclient import TestClient



def test_interruption_and_replanning_flow(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 6})

    interruption_events = phase3_seeded_client.get(
        f"/scenarios/{scenario_id}/timeline",
        params={"event_type": "interruption"},
    ).json()
    plan_events = phase3_seeded_client.get(
        f"/scenarios/{scenario_id}/timeline",
        params={"event_type": "plan_change"},
    ).json()

    assert plan_events
    assert any(event["event_type"] == "interruption" for event in interruption_events) or any(
        "seek_safety" in str(event["payload"]) for event in plan_events
    )
