from fastapi.testclient import TestClient


def test_relationship_updates_after_run(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    before = seeded_client.get(f"/scenarios/{scenario_id}/relationships").json()
    seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 2})
    after = seeded_client.get(f"/scenarios/{scenario_id}/relationships").json()

    assert len(after) >= len(before)
    assert any(row["last_updated_tick"] >= 1 for row in after)
    assert any(row["last_interaction_at"] is not None for row in after)


def test_relationship_endpoint_agent_filter(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    agents = seeded_client.get(f"/scenarios/{scenario_id}/agents").json()
    focus_agent = agents[0]["id"]
    seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1})

    filtered = seeded_client.get(
        f"/scenarios/{scenario_id}/relationships",
        params={"agent_id": focus_agent},
    )
    assert filtered.status_code == 200
    for row in filtered.json():
        assert focus_agent in {row["source_agent_id"], row["target_agent_id"]}
