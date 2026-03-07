from __future__ import annotations

from app.agents.response_parser import parse_structured_response
from app.schemas.decision_engine import DecisionConstraints, FallbackReason, ParserStatus


def test_parser_accepts_valid_json_response() -> None:
    raw = '{"action":"observe","intent":"observe","emotional_tone":"neutral","rationale":"observe","confidence":0.8}'
    result = parse_structured_response(raw)
    assert result.success is True
    assert result.parser_status == ParserStatus.VALID
    assert result.decision is not None


def test_parser_rejects_invalid_json() -> None:
    result = parse_structured_response("not json")
    assert result.success is False
    assert result.parser_status == ParserStatus.INVALID_JSON
    assert result.fallback_reason == FallbackReason.INVALID_JSON


def test_parser_rejects_schema_failures() -> None:
    result = parse_structured_response('{"action":"invalid","intent":"observe","emotional_tone":"neutral","rationale":"x"}')
    assert result.success is False
    assert result.parser_status == ParserStatus.SCHEMA_ERROR
    assert result.fallback_reason == FallbackReason.SCHEMA_ERROR


def test_parser_rejects_constraint_failures() -> None:
    raw = '{"action":"move","intent":"observe","emotional_tone":"neutral","rationale":"move","target_zone_id":"zone-2"}'
    constraints = DecisionConstraints(allowed_zone_ids=["zone-1"])
    result = parse_structured_response(raw, constraints=constraints)
    assert result.success is False
    assert result.parser_status == ParserStatus.LEGALITY_ERROR
    assert result.fallback_reason == FallbackReason.WORLD_CONSTRAINT
