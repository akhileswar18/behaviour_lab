from fastapi.testclient import TestClient


def _first_identity(client: TestClient) -> dict:
    identities = client.get("/analytics/agents").json()
    assert identities
    return identities[0]


def test_agent_observatory_overview_vs_scenario_mode(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 6})

    identity = _first_identity(phase3_seeded_client)

    overview = phase3_seeded_client.get(
        "/analytics/agent-observatory",
        params={"identity_key": identity["identity_key"], "tick_from": 1, "tick_to": 6},
    ).json()
    assert overview["mode"] == "overview"
    assert overview["scope_label"] == "All scenarios"
    assert overview["scope_notes"]
    assert overview["behavioral_trends"] is not None

    scoped = phase3_seeded_client.get(
        "/analytics/agent-observatory",
        params={
            "identity_key": identity["identity_key"],
            "scenario_id": identity["latest_scenario_id"],
            "tick_from": 1,
            "tick_to": 6,
        },
    ).json()
    assert scoped["mode"] == "scenario"
    assert "Scenario:" in scoped["scope_label"]
    assert scoped["selected_scenario_id"] == identity["latest_scenario_id"]


def test_agent_observatory_matches_persisted_message_counts(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 6})

    agent_id = phase3_seeded_client.get(f"/scenarios/{scenario_id}/agents").json()[0]["id"]
    compat = phase3_seeded_client.get(
        f"/scenarios/{scenario_id}/analytics/agent/{agent_id}",
        params={"tick_from": 1, "tick_to": 6},
    ).json()
    messages = phase3_seeded_client.get(
        f"/scenarios/{scenario_id}/messages",
        params={"agent_id": agent_id, "tick_from": 1, "tick_to": 6},
    ).json()

    sent = sum(1 for row in messages if row["sender_agent_id"] == agent_id)
    received = sum(1 for row in messages if row["receiver_agent_id"] == agent_id)

    assert compat["interaction_metrics"]["messages_sent"] == sent
    assert compat["interaction_metrics"]["messages_received"] == received
    assert compat["action_mix"] is not None
    assert compat["needs_history"] is not None


def test_agent_observatory_memory_and_trend_payloads(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 5})

    identity = _first_identity(phase3_seeded_client)
    analytics = phase3_seeded_client.get(
        "/analytics/agent-observatory",
        params={"identity_key": identity["identity_key"], "scenario_id": identity["latest_scenario_id"]},
    ).json()

    assert analytics["memory_influences"] is not None
    assert analytics["memory_summary"] is not None
    assert analytics["memory_influence_trend"] is not None
    assert analytics["behavioral_trends"] is not None
