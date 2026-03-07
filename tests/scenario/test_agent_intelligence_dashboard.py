from fastapi.testclient import TestClient


def test_agent_intelligence_mode_switch_and_behavior_sections(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 8})

    identities = phase3_seeded_client.get("/analytics/agents").json()
    assert identities
    identity = identities[0]

    overview = phase3_seeded_client.get(
        "/analytics/agent-observatory",
        params={"identity_key": identity["identity_key"]},
    ).json()

    assert overview["mode"] == "overview"
    assert overview["agent"]["name"]
    assert len(overview["needs"]) == 3
    assert {"hunger", "safety_need", "social_need"}.issubset(
        set(overview["needs_history"][0].keys()) if overview["needs_history"] else {"hunger", "safety_need", "social_need"}
    )
    assert "messages_sent" in overview["interaction_metrics"]
    assert "messages_received" in overview["interaction_metrics"]

    scenario_scoped = phase3_seeded_client.get(
        "/analytics/agent-observatory",
        params={
            "identity_key": identity["identity_key"],
            "scenario_id": identity["latest_scenario_id"],
            "tick_from": 1,
            "tick_to": 8,
        },
    ).json()

    assert scenario_scoped["mode"] == "scenario"
    assert scenario_scoped["selected_scenario_id"] == identity["latest_scenario_id"]
    assert scenario_scoped["decisions"] or scenario_scoped["recent_events"]
    assert scenario_scoped["action_mix"] is not None
    assert scenario_scoped["behavioral_trends"] is not None
    assert scenario_scoped["plan_history"] is not None
