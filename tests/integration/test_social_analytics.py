from fastapi.testclient import TestClient


def test_social_analytics_matches_message_feed_counts(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 8})

    social = phase3_seeded_client.get(
        f"/scenarios/{scenario_id}/analytics/social",
        params={"tick_from": 1, "tick_to": 8},
    ).json()
    messages = phase3_seeded_client.get(
        f"/scenarios/{scenario_id}/messages",
        params={"tick_from": 1, "tick_to": 8},
    ).json()

    assert len(social["communication_feed"]) == len(messages)
    assert social["cooperation_conflict_summary"]["total_messages"] == len(messages)
    assert social["relationship_graph"] is not None


def test_social_analytics_exposes_per_agent_metrics(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 8})

    social = phase3_seeded_client.get(f"/scenarios/{scenario_id}/analytics/social").json()

    assert social["interaction_metrics"]
    first = social["interaction_metrics"][0]
    assert {"agent_id", "agent_name", "messages_sent", "messages_received", "cooperation_events", "conflict_events"}.issubset(first.keys())
