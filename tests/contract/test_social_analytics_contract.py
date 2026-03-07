from fastapi.testclient import TestClient


def test_social_analytics_contract(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 6})

    response = phase3_seeded_client.get(f"/scenarios/{scenario_id}/analytics/social")

    assert response.status_code == 200
    payload = response.json()
    assert {
        "scenario_id",
        "communication_feed",
        "relationship_graph",
        "interaction_metrics",
        "relationship_history",
        "causal_chains",
        "cooperation_conflict_summary",
    }.issubset(payload.keys())
    if payload["relationship_graph"]:
        assert {
            "source_agent_id",
            "target_agent_id",
            "source_agent_name",
            "target_agent_name",
            "trust",
            "affinity",
            "stance",
        }.issubset(payload["relationship_graph"][0].keys())
