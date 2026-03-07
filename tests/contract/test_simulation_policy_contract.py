from __future__ import annotations

from fastapi.testclient import TestClient


def test_simulation_run_response_contains_policy_fields(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    response = seeded_client.post(
        f"/scenarios/{scenario_id}/run",
        json={"ticks": 1, "policy_mode": "deterministic"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "policy_mode" in body
    assert "fallback_count" in body
    assert "llm_decision_count" in body
    assert "deterministic_decision_count" in body
    assert isinstance(body["tick_results"], list)
