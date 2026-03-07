from fastapi.testclient import TestClient


def test_agent_analytics_contract(phase3_seeded_client: TestClient) -> None:
    identities_response = phase3_seeded_client.get("/analytics/agents")
    assert identities_response.status_code == 200
    identities = identities_response.json()
    assert identities
    identity = identities[0]
    assert {"identity_key", "name", "persona_label", "available_scenarios"}.issubset(identity.keys())

    response = phase3_seeded_client.get(
        "/analytics/agent-observatory",
        params={"identity_key": identity["identity_key"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert {
        "scenario_id",
        "mode",
        "scope_label",
        "available_scenarios",
        "agent",
        "needs",
        "needs_history",
        "active_goal",
        "active_intention",
        "plan_history",
        "decisions",
        "action_mix",
        "memory_influences",
        "memory_summary",
        "memory_influence_trend",
        "relationships",
        "interaction_metrics",
        "behavioral_trends",
        "recent_events",
    }.issubset(payload.keys())
    assert {
        "id",
        "name",
        "persona_label",
        "communication_style",
        "zone_name",
        "inventory",
    }.issubset(payload["agent"].keys())
    assert {
        "messages_sent",
        "messages_received",
        "cooperation_events",
        "conflict_events",
        "goal_completion_rate",
        "interruption_count",
        "completed_goals",
    }.issubset(payload["interaction_metrics"].keys())

    # Compatibility wrapper still supported.
    scenario_id = identity["latest_scenario_id"]
    agent_id = identity["latest_agent_id"]
    compat = phase3_seeded_client.get(f"/scenarios/{scenario_id}/analytics/agent/{agent_id}")
    assert compat.status_code == 200
