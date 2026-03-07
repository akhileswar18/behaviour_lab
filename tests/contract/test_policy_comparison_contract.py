from __future__ import annotations

from fastapi.testclient import TestClient


def test_policy_comparison_contract_fields(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    response = seeded_client.post(
        f"/scenarios/{scenario_id}/compare-rerun",
        json={
            "ticks": 1,
            "variant_name": "contract-check",
            "base_policy_mode": "deterministic",
            "variant_policy_mode": "hybrid",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "base_policy_mode" in body
    assert "variant_policy_mode" in body
    assert "comparison" in body
    assert "differences" in body["comparison"]
    assert "fallback_count_delta" in body["comparison"]["differences"]
