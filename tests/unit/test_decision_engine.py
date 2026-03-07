from __future__ import annotations

from uuid import UUID

from app.agents.decision_engine import DecisionEngine
from app.schemas.decision_engine import (
    DecisionContext,
    DecisionSource,
    FallbackReason,
    LlmConfig,
    LlmInvocation,
    ParserStatus,
    PolicyMode,
)


def _context() -> DecisionContext:
    return DecisionContext(
        scenario_id=UUID(int=1),
        agent_id=UUID(int=2),
        agent_name="Ava",
        tick_number=1,
        persona={
            "label": "Mediator",
            "communication_style": "diplomatic",
            "risk_tolerance": 0.3,
            "cooperation_tendency": 0.8,
            "memory_sensitivity": 0.7,
            "emotional_bias": 0.0,
        },
        needs={"hunger": 0.2, "safety_need": 0.1, "social_need": 0.4},
        observed_events=[],
        planning_context={"action": "wait"},
    )


class _SuccessPolicy:
    def invoke(self, context: DecisionContext, config: LlmConfig) -> LlmInvocation:
        _ = context, config
        return LlmInvocation(
            success=True,
            raw_response='{"action":"observe","intent":"observe","emotional_tone":"neutral","rationale":"scan","confidence":0.7}',
            provider="mock",
            model="mock-model",
            latency_ms=12,
        )


class _FailPolicy:
    def invoke(self, context: DecisionContext, config: LlmConfig) -> LlmInvocation:
        _ = context, config
        return LlmInvocation(
            success=False,
            raw_response="",
            provider="mock",
            model="mock-model",
            latency_ms=20,
            error="timeout",
            parser_status=ParserStatus.TIMEOUT,
            fallback_reason=FallbackReason.TIMEOUT,
        )


def test_routing_deterministic_mode() -> None:
    engine = DecisionEngine(llm_policy=_SuccessPolicy())
    result = engine.resolve(_context(), mode=PolicyMode.DETERMINISTIC)
    assert result.decision_source == DecisionSource.DETERMINISTIC
    assert result.parser_status == ParserStatus.NOT_ATTEMPTED


def test_routing_llm_mode() -> None:
    engine = DecisionEngine(llm_policy=_SuccessPolicy())
    result = engine.resolve(_context(), mode=PolicyMode.LLM)
    assert result.decision_source == DecisionSource.LLM
    assert result.decision.action == "observe"
    assert result.parser_status == ParserStatus.VALID


def test_routing_hybrid_falls_back_on_failure() -> None:
    engine = DecisionEngine(llm_policy=_FailPolicy())
    result = engine.resolve(_context(), mode=PolicyMode.HYBRID)
    assert result.decision_source == DecisionSource.FALLBACK_DETERMINISTIC
    assert result.fallback_reason == FallbackReason.TIMEOUT
    assert result.parser_status == ParserStatus.TIMEOUT
