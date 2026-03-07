from __future__ import annotations

from fastapi.testclient import TestClient


def test_phase4_hybrid_smoke_flow(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]
    run = seeded_client.post(
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
    assert run.status_code == 200
    run_body = run.json()
    assert run_body["policy_mode"] == "hybrid"
    assert len(run_body["tick_results"]) == 2

    identities = seeded_client.get("/analytics/agents").json()
    observatory = seeded_client.get(
        "/analytics/agent-observatory",
        params={"identity_key": identities[0]["identity_key"]},
    )
    assert observatory.status_code == 200
    obs = observatory.json()
    assert "decisions" in obs
    assert "interaction_metrics" in obs
