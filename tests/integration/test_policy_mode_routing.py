from __future__ import annotations

from fastapi.testclient import TestClient


def test_run_endpoint_routes_by_policy_mode(seeded_client: TestClient) -> None:
    scenario_id = seeded_client.get("/scenarios").json()[0]["id"]

    deterministic = seeded_client.post(
        f"/scenarios/{scenario_id}/run",
        json={"ticks": 1, "policy_mode": "deterministic"},
    )
    assert deterministic.status_code == 200
    assert deterministic.json()["policy_mode"] == "deterministic"

    hybrid = seeded_client.post(
        f"/scenarios/{scenario_id}/run",
        json={
            "ticks": 1,
            "policy_mode": "hybrid",
            "llm_config": {
                "provider": "openai_compatible",
                "endpoint": "http://127.0.0.1:1/v1/chat/completions",
                "timeout_seconds": 0.2,
            },
        },
    )
    assert hybrid.status_code == 200
    assert hybrid.json()["policy_mode"] == "hybrid"

    timeline = seeded_client.get(
        f"/scenarios/{scenario_id}/timeline",
        params={"event_type": "decision"},
    ).json()
    assert timeline
    assert any("decision_source" in (row.get("payload") or {}) for row in timeline)
