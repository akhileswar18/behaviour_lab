from __future__ import annotations

from fastapi.testclient import TestClient


def test_phase4_policy_compare_flow(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    compare = seeded_client.post(
        f"/scenarios/{scenario_id}/compare-rerun",
        json={
            "ticks": 2,
            "variant_name": "phase4-compare",
            "base_policy_mode": "deterministic",
            "variant_policy_mode": "llm",
            "variant_llm_config": {
                "provider": "openai_compatible",
                "endpoint": "http://127.0.0.1:1/v1/chat/completions",
                "timeout_seconds": 0.2,
            },
        },
    )
    assert compare.status_code == 200
    body = compare.json()
    base_id = body["base_scenario_id"]
    variant_id = body["variant_scenario_id"]

    direct_compare = seeded_client.get(f"/scenarios/{base_id}/compare/{variant_id}")
    assert direct_compare.status_code == 200
    metrics = direct_compare.json()["metrics"]
    assert "fallback_count_delta" in metrics
    assert "llm_decision_delta" in metrics
