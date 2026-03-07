from __future__ import annotations

from fastapi.testclient import TestClient


def test_phase4_fallback_reproducible_under_same_failure_config(
    seeded_client: TestClient,
) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    request_payload = {
        "ticks": 2,
        "policy_mode": "llm",
        "llm_config": {
            "provider": "openai_compatible",
            "endpoint": "http://127.0.0.1:1/v1/chat/completions",
            "timeout_seconds": 0.2,
        },
    }

    run_one = seeded_client.post(f"/scenarios/{scenario_id}/run", json=request_payload).json()
    first_fallback = int(run_one["fallback_count"])

    seeded_client.post(f"/scenarios/{scenario_id}/reset")
    seeded_client.post(f"/scenarios/{scenario_id}/run", json={"ticks": 1, "policy_mode": "deterministic"})
    run_two = seeded_client.post(f"/scenarios/{scenario_id}/run", json=request_payload).json()
    second_fallback = int(run_two["fallback_count"])

    assert first_fallback >= 1
    assert second_fallback >= 1
