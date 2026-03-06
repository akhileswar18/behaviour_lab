from fastapi.testclient import TestClient


def test_compare_rerun_is_repeatable_for_same_overrides(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    payload = {
        "ticks": 2,
        "variant_name": "repeatability-check",
        "persona_overrides": {
            "Ben": {"risk_tolerance": 0.85},
        },
    }

    first = seeded_client.post(f"/scenarios/{scenario_id}/compare-rerun", json=payload)
    assert first.status_code == 200
    second = seeded_client.post(f"/scenarios/{scenario_id}/compare-rerun", json=payload)
    assert second.status_code == 200

    first_diff = first.json()["comparison"]["differences"]
    second_diff = second.json()["comparison"]["differences"]
    assert first_diff["decision_count_delta"] == second_diff["decision_count_delta"]
    assert first_diff["message_count_delta"] == second_diff["message_count_delta"]
    assert first_diff["relationship_avg_trust_delta"] == second_diff["relationship_avg_trust_delta"]
