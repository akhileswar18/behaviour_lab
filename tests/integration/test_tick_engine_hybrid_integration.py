from __future__ import annotations

from fastapi.testclient import TestClient


def test_hybrid_mode_keeps_tick_pipeline_stable(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    response = seeded_client.post(
        f"/scenarios/{scenario_id}/run",
        json={
            "ticks": 3,
            "policy_mode": "hybrid",
            "llm_config": {
                "provider": "openai_compatible",
                "endpoint": "http://127.0.0.1:1/v1/chat/completions",
                "timeout_seconds": 0.2,
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["tick_results"]) == 3
    assert body["end_tick"] >= 3

    timeline = seeded_client.get(f"/scenarios/{scenario_id}/timeline").json()
    assert any(event["event_type"] == "decision" for event in timeline)
    assert any("decision_source" in (event.get("payload") or {}) for event in timeline)
