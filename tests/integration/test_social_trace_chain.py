from fastapi.testclient import TestClient


def test_social_causal_chain_visible_in_timeline(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 2})

    message_events = seeded_client.get(
        f"/scenarios/{scenario_id}/timeline",
        params={"event_type": "message"},
    ).json()
    relationship_events = seeded_client.get(
        f"/scenarios/{scenario_id}/timeline",
        params={"event_type": "relationship_update"},
    ).json()

    assert message_events
    assert relationship_events
    assert any("message_id" in event["payload"] for event in message_events)
    assert any("decision_id" in event["payload"] for event in relationship_events)
