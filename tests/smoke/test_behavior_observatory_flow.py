from fastapi.testclient import TestClient


def test_behavior_observatory_agent_cockpit_flow(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    run_response = phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 6})
    assert run_response.status_code == 200

    identities_response = phase3_seeded_client.get("/analytics/agents")
    assert identities_response.status_code == 200
    identities = identities_response.json()
    assert identities
    identity = identities[0]

    observatory_response = phase3_seeded_client.get(
        "/analytics/agent-observatory",
        params={"identity_key": identity["identity_key"], "scenario_id": identity["latest_scenario_id"]},
    )
    assert observatory_response.status_code == 200
    snapshot = observatory_response.json()
    assert snapshot["agent"]["name"]
    assert "interaction_metrics" in snapshot
