from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from app.schemas.decision_engine import (
    DecisionConstraints,
    FallbackReason,
    ParseResult,
    ParserStatus,
    StructuredDecision,
)


JSON_BLOCK = re.compile(r"\{.*\}", flags=re.DOTALL)


def _extract_json(raw_response: str) -> dict[str, Any]:
    if not raw_response:
        raise ValueError("empty_response")
    stripped = raw_response.strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = JSON_BLOCK.search(stripped)
        if not match:
            raise ValueError("invalid_json") from None
        return json.loads(match.group(0))


def _validate_legality(
    decision: StructuredDecision,
    constraints: DecisionConstraints | None,
) -> tuple[bool, str | None]:
    if constraints is None:
        return True, None

    if decision.action not in constraints.allowed_actions:
        return False, f"action_not_allowed:{decision.action}"

    if decision.target_zone_id and constraints.allowed_zone_ids:
        if decision.target_zone_id not in constraints.allowed_zone_ids:
            return False, f"unknown_zone:{decision.target_zone_id}"

    if decision.target_resource_id and constraints.allowed_resource_ids:
        if decision.target_resource_id not in constraints.allowed_resource_ids:
            return False, f"unknown_resource:{decision.target_resource_id}"

    if decision.target_agent_id and constraints.allowed_target_agent_ids:
        if decision.target_agent_id not in constraints.allowed_target_agent_ids:
            return False, f"unknown_target_agent:{decision.target_agent_id}"

    return True, None


def parse_structured_response(
    raw_response: str,
    constraints: DecisionConstraints | None = None,
) -> ParseResult:
    try:
        payload = _extract_json(raw_response)
    except ValueError as exc:
        return ParseResult(
            success=False,
            parser_status=ParserStatus.INVALID_JSON,
            fallback_reason=FallbackReason.INVALID_JSON,
            error=str(exc),
        )

    try:
        decision = StructuredDecision.model_validate(payload)
    except ValidationError as exc:
        return ParseResult(
            success=False,
            parser_status=ParserStatus.SCHEMA_ERROR,
            fallback_reason=FallbackReason.SCHEMA_ERROR,
            error=str(exc),
        )

    legal, error = _validate_legality(decision, constraints)
    if not legal:
        fallback_reason = (
            FallbackReason.ILLEGAL_ACTION
            if error and error.startswith("action_not_allowed")
            else FallbackReason.WORLD_CONSTRAINT
        )
        return ParseResult(
            success=False,
            parser_status=ParserStatus.LEGALITY_ERROR,
            fallback_reason=fallback_reason,
            error=error,
        )

    return ParseResult(success=True, parser_status=ParserStatus.VALID, decision=decision)
