from __future__ import annotations

from fastapi.testclient import TestClient


def test_agent_observability_includes_decision_source_and_fallback_metadata(
    seeded_client: TestClient,
) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    seeded_client.post(
        f"/scenarios/{scenario_id}/run",
        json={
            "ticks": 2,
            "policy_mode": "hybrid",
            "llm_config": {
                "provider": "openai_compatible",
                "endpoint": "http://127.0.0.1:1/v1/chat/completions",
                "timeout_seconds": 0.2,
            },
        },
    )
    identities = seeded_client.get("/analytics/agents").json()
    payload = seeded_client.get(
        "/analytics/agent-observatory",
        params={"identity_key": identities[0]["identity_key"]},
    ).json()
    assert "interaction_metrics" in payload
    assert "fallback_count" in payload["interaction_metrics"]
    assert payload["decisions"]
    decision = payload["decisions"][0]
    assert "decision_source" in decision
    assert "parser_status" in decision
    assert "fallback_reason" in decision
