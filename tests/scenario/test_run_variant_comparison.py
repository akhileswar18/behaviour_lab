from fastapi.testclient import TestClient


def test_compare_rerun_persona_variant(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    payload = {
        "ticks": 3,
        "variant_name": "risk-heavy-ava",
        "persona_overrides": {
            "Ava": {"risk_tolerance": 0.95, "cooperation_tendency": 0.2},
        },
    }
    response = seeded_client.post(f"/scenarios/{scenario_id}/compare-rerun", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "base_scenario_id" in body
    assert "variant_scenario_id" in body
    assert "comparison" in body
    assert "differences" in body["comparison"]
