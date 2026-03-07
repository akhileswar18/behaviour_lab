from __future__ import annotations

from uuid import UUID

from app.agents.prompt_builder import build_prompt
from app.schemas.decision_engine import DecisionContext


def _context() -> DecisionContext:
    events = [
        {"tick_number": tick, "event_type": "world_event", "content": f"event-{tick}", "payload": {}}
        for tick in range(10)
    ]
    memories = [
        {
            "tick_number": tick,
            "memory_type": "decision",
            "content": f"memory-{tick}",
            "relevance_score": tick / 10,
            "salience": tick / 10,
        }
        for tick in range(10)
    ]
    return DecisionContext(
        scenario_id=UUID(int=1),
        agent_id=UUID(int=2),
        agent_name="Ava",
        tick_number=6,
        persona={"label": "Mediator", "communication_style": "diplomatic"},
        needs={"hunger": 0.4, "safety_need": 0.2, "social_need": 0.3},
        observed_events=events,
        recalled_memories=memories,
        relationships=[{"target_agent_id": "x", "trust": 0.5, "affinity": 0.4, "stance": "ally"}],
        local_resources=[{"id": "r1", "resource_type": "food", "quantity": 2, "status": "available"}],
        planning_context={"action": "observe"},
    )


def test_prompt_context_contains_required_sections() -> None:
    result = build_prompt(_context())
    prompt = result.prompt
    assert "persona" in prompt
    assert "needs" in prompt
    assert "recent_world_events" in prompt
    assert "recalled_memories" in prompt
    assert result.summary["event_count"] <= 6
    assert result.summary["memory_count"] <= 6


def test_prompt_summary_reports_truncation() -> None:
    result = build_prompt(_context())
    assert result.summary["truncated"]["events"] >= 1
    assert result.summary["truncated"]["memories"] >= 1
