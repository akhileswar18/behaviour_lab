from __future__ import annotations

from app.agents.response_parser import parse_structured_response
from app.schemas.decision_engine import DecisionConstraints, FallbackReason, ParserStatus


def test_illegal_action_is_rejected_before_execution() -> None:
    raw = '{"action":"move","intent":"observe","emotional_tone":"neutral","rationale":"move"}'
    constraints = DecisionConstraints(allowed_actions=["observe", "wait"])
    result = parse_structured_response(raw, constraints=constraints)
    assert result.success is False
    assert result.parser_status == ParserStatus.LEGALITY_ERROR
    assert result.fallback_reason == FallbackReason.ILLEGAL_ACTION


def test_unknown_target_agent_is_rejected() -> None:
    raw = '{"action":"propose","intent":"propose","emotional_tone":"neutral","rationale":"talk","target_agent_id":"agent-b"}'
    constraints = DecisionConstraints(allowed_target_agent_ids=["agent-a"])
    result = parse_structured_response(raw, constraints=constraints)
    assert result.success is False
    assert result.parser_status == ParserStatus.LEGALITY_ERROR
    assert result.fallback_reason == FallbackReason.WORLD_CONSTRAINT
