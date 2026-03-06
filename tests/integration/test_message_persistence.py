from fastapi.testclient import TestClient


def test_message_persistence_after_run(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 2})

    messages = seeded_client.get(f"/scenarios/{scenario_id}/messages")
    assert messages.status_code == 200
    rows = messages.json()
    assert rows
    assert all(row["tick_number"] >= 0 for row in rows)
    assert all(row["intent"] for row in rows)
    assert all(row["emotional_tone"] for row in rows)


def test_message_query_filters(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 3})

    filtered = seeded_client.get(
        f"/scenarios/{scenario_id}/messages",
        params={"tick_from": 2, "tick_to": 3, "intent": "propose"},
    )
    assert filtered.status_code == 200
    for row in filtered.json():
        assert 2 <= row["tick_number"] <= 3
        assert row["intent"] == "propose"
