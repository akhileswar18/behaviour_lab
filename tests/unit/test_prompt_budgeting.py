from __future__ import annotations

from uuid import UUID

from app.agents.prompt_builder import build_prompt
from app.schemas.decision_engine import DecisionContext


def test_prompt_budgeting_caps_event_and_memory_blocks() -> None:
    context = DecisionContext(
        scenario_id=UUID(int=1),
        agent_id=UUID(int=2),
        agent_name="Ava",
        tick_number=5,
        persona={"label": "Mediator"},
        needs={"hunger": 0.2, "safety_need": 0.1, "social_need": 0.4},
        observed_events=[{"tick_number": idx, "event_type": "world_event", "content": str(idx), "payload": {}} for idx in range(20)],
        recalled_memories=[
            {
                "tick_number": idx,
                "memory_type": "decision",
                "content": f"memory {idx}",
                "relevance_score": float(idx) / 20.0,
                "salience": float(idx) / 20.0,
            }
            for idx in range(20)
        ],
    )
    result = build_prompt(context)
    assert result.summary["event_count"] == 6
    assert result.summary["memory_count"] == 6
    assert result.summary["truncated"]["events"] == 14
    assert result.summary["truncated"]["memories"] == 14
