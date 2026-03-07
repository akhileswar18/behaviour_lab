from __future__ import annotations

from app.agents.model_adapter import ModelAdapter, get_model_adapter
from app.agents.prompt_builder import PromptBuildResult, build_prompt
from app.schemas.decision_engine import (
    FallbackReason,
    LlmConfig,
    LlmInvocation,
    ParserStatus,
)


class LlmPolicy:
    def __init__(self, adapter: ModelAdapter | None = None):
        self.adapter = adapter

    def invoke(self, context, config: LlmConfig) -> LlmInvocation:
        prompt_result: PromptBuildResult = build_prompt(context)
        adapter = self.adapter or get_model_adapter(config.provider)
        response = adapter.generate(prompt_result.prompt, config)
        if not response.success:
            status = ParserStatus.TIMEOUT if "timeout" in str(response.error).lower() else ParserStatus.PROVIDER_ERROR
            reason = FallbackReason.TIMEOUT if status == ParserStatus.TIMEOUT else FallbackReason.PROVIDER_ERROR
            return LlmInvocation(
                success=False,
                raw_response="",
                provider=response.provider,
                model=response.model,
                latency_ms=response.latency_ms,
                error=response.error,
                parser_status=status,
                fallback_reason=reason,
                prompt_summary=prompt_result.summary,
                prompt_hash=prompt_result.prompt_hash,
            )

        return LlmInvocation(
            success=True,
            raw_response=response.text,
            provider=response.provider,
            model=response.model,
            latency_ms=response.latency_ms,
            prompt_summary=prompt_result.summary,
            prompt_hash=prompt_result.prompt_hash,
        )
