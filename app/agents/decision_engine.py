from __future__ import annotations

from app.agents.decision_policy import choose_structured_action
from app.agents.llm_policy import LlmPolicy
from app.agents.response_parser import parse_structured_response
from app.schemas.decision_engine import (
    DecisionConstraints,
    DecisionSource,
    LlmConfig,
    ParserStatus,
    PolicyMode,
    StructuredDecisionResult,
)


class DecisionEngine:
    def __init__(self, llm_policy: LlmPolicy | None = None):
        self.llm_policy = llm_policy or LlmPolicy()

    def resolve(
        self,
        context,
        mode: PolicyMode,
        llm_config: LlmConfig | None = None,
        constraints: DecisionConstraints | None = None,
    ) -> StructuredDecisionResult:
        if mode == PolicyMode.DETERMINISTIC:
            deterministic = choose_structured_action(context)
            return StructuredDecisionResult(
                decision=deterministic,
                decision_source=DecisionSource.DETERMINISTIC,
                parser_status=ParserStatus.NOT_ATTEMPTED,
            )

        llm_config = llm_config or LlmConfig()
        llm_attempt = self.llm_policy.invoke(context, llm_config)
        if not llm_attempt.success:
            deterministic = choose_structured_action(context)
            return StructuredDecisionResult(
                decision=deterministic,
                decision_source=DecisionSource.FALLBACK_DETERMINISTIC,
                parser_status=llm_attempt.parser_status,
                fallback_reason=llm_attempt.fallback_reason,
                llm_error=llm_attempt.error,
                llm_provider=llm_attempt.provider,
                llm_model=llm_attempt.model,
                llm_latency_ms=llm_attempt.latency_ms,
                prompt_summary=llm_attempt.prompt_summary,
                prompt_hash=llm_attempt.prompt_hash,
            )

        parsed = parse_structured_response(llm_attempt.raw_response, constraints=constraints)
        if parsed.success and parsed.decision is not None:
            return StructuredDecisionResult(
                decision=parsed.decision,
                decision_source=DecisionSource.LLM,
                parser_status=ParserStatus.VALID,
                llm_provider=llm_attempt.provider,
                llm_model=llm_attempt.model,
                llm_latency_ms=llm_attempt.latency_ms,
                prompt_summary=llm_attempt.prompt_summary,
                prompt_hash=llm_attempt.prompt_hash,
            )

        deterministic = choose_structured_action(context)
        return StructuredDecisionResult(
            decision=deterministic,
            decision_source=DecisionSource.FALLBACK_DETERMINISTIC,
            parser_status=parsed.parser_status,
            fallback_reason=parsed.fallback_reason,
            llm_error=parsed.error,
            llm_provider=llm_attempt.provider,
            llm_model=llm_attempt.model,
            llm_latency_ms=llm_attempt.latency_ms,
            prompt_summary=llm_attempt.prompt_summary,
            prompt_hash=llm_attempt.prompt_hash,
        )
