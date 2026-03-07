from __future__ import annotations

from fastapi.testclient import TestClient


def test_llm_timeout_falls_back_to_deterministic(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    response = seeded_client.post(
        f"/scenarios/{scenario_id}/run",
        json={
            "ticks": 1,
            "policy_mode": "llm",
            "llm_config": {
                "provider": "openai_compatible",
                "endpoint": "http://127.0.0.1:1/v1/chat/completions",
                "timeout_seconds": 0.2,
                "model": "test-model",
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["policy_mode"] == "llm"
    assert body["fallback_count"] >= 1

    timeline = seeded_client.get(f"/scenarios/{scenario_id}/timeline", params={"event_type": "interruption"}).json()
    assert any(event["content"] == "llm_fallback_triggered" for event in timeline)
