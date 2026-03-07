from __future__ import annotations

from fastapi.testclient import TestClient


def test_compare_rerun_includes_policy_metadata_and_fallback_deltas(
    seeded_client: TestClient,
) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    response = seeded_client.post(
        f"/scenarios/{scenario_id}/compare-rerun",
        json={
            "ticks": 2,
            "variant_name": "phase4-policy-check",
            "base_policy_mode": "deterministic",
            "variant_policy_mode": "hybrid",
            "variant_llm_config": {
                "provider": "openai_compatible",
                "endpoint": "http://127.0.0.1:1/v1/chat/completions",
                "timeout_seconds": 0.2,
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["base_policy_mode"] == "deterministic"
    assert body["variant_policy_mode"] == "hybrid"
    deltas = body["comparison"]["differences"]
    assert "fallback_count_delta" in deltas
    assert "llm_decision_delta" in deltas
