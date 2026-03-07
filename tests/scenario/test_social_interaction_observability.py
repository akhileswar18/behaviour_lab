from fastapi.testclient import TestClient


def test_social_observability_reveals_causal_chains(phase3_seeded_client: TestClient) -> None:
    scenario_id = phase3_seeded_client.get("/scenarios").json()[0]["id"]
    phase3_seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 10})

    social = phase3_seeded_client.get(f"/scenarios/{scenario_id}/analytics/social").json()

    assert social["causal_chains"]
    assert any(chain["relationship_event_id"] is not None for chain in social["causal_chains"])
    assert any(chain["memory_ids"] for chain in social["causal_chains"])
