from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.social import (
    ALLOWED_EMOTIONAL_TONES,
    ALLOWED_MESSAGE_INTENTS,
    ALLOWED_SOCIAL_ACTIONS,
)


class PolicyMode(StrEnum):
    DETERMINISTIC = "deterministic"
    LLM = "llm"
    HYBRID = "hybrid"


class DecisionSource(StrEnum):
    DETERMINISTIC = "deterministic"
    LLM = "llm"
    FALLBACK_DETERMINISTIC = "fallback_deterministic"


class ParserStatus(StrEnum):
    NOT_ATTEMPTED = "not_attempted"
    VALID = "valid"
    INVALID_JSON = "invalid_json"
    SCHEMA_ERROR = "schema_error"
    LEGALITY_ERROR = "legality_error"
    PROVIDER_ERROR = "provider_error"
    TIMEOUT = "timeout"


class FallbackReason(StrEnum):
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"
    INVALID_JSON = "invalid_json"
    SCHEMA_ERROR = "schema_error"
    ILLEGAL_ACTION = "illegal_action"
    WORLD_CONSTRAINT = "world_constraint"


class LlmConfig(BaseModel):
    provider: str | None = None
    model: str | None = None
    endpoint: str | None = None
    timeout_seconds: float = Field(default=4.0, gt=0.1, le=60.0)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=32, le=2048)
    api_key: str | None = None
    debug_store_prompt: bool = False


class StructuredDecision(BaseModel):
    action: str
    intent: str
    emotional_tone: str
    rationale: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    target_agent_id: str | None = None
    target_zone_id: str | None = None
    target_resource_id: str | None = None

    @field_validator("action")
    @classmethod
    def validate_action(cls, value: str) -> str:
        if value not in ALLOWED_SOCIAL_ACTIONS:
            raise ValueError(f"Unsupported action: {value}")
        return value

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, value: str) -> str:
        if value not in ALLOWED_MESSAGE_INTENTS:
            raise ValueError(f"Unsupported intent: {value}")
        return value

    @field_validator("emotional_tone")
    @classmethod
    def validate_tone(cls, value: str) -> str:
        if value not in ALLOWED_EMOTIONAL_TONES:
            raise ValueError(f"Unsupported emotional tone: {value}")
        return value


class DecisionContext(BaseModel):
    scenario_id: UUID
    agent_id: UUID
    agent_name: str
    tick_number: int
    persona: dict[str, Any] = Field(default_factory=dict)
    needs: dict[str, float] = Field(default_factory=dict)
    mood: str = "neutral"
    zone: dict[str, Any] | None = None
    active_goal: dict[str, Any] | None = None
    active_intention: dict[str, Any] | None = None
    planning_context: dict[str, Any] = Field(default_factory=dict)
    observed_events: list[dict[str, Any]] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    recalled_memories: list[dict[str, Any]] = Field(default_factory=list)
    local_resources: list[dict[str, Any]] = Field(default_factory=list)


class DecisionConstraints(BaseModel):
    allowed_actions: list[str] = Field(default_factory=lambda: list(ALLOWED_SOCIAL_ACTIONS))
    allowed_zone_ids: list[str] = Field(default_factory=list)
    allowed_resource_ids: list[str] = Field(default_factory=list)
    allowed_target_agent_ids: list[str] = Field(default_factory=list)


class ParseResult(BaseModel):
    success: bool
    parser_status: ParserStatus
    decision: StructuredDecision | None = None
    error: str | None = None
    fallback_reason: FallbackReason | None = None


class LlmInvocation(BaseModel):
    success: bool
    raw_response: str = ""
    provider: str | None = None
    model: str | None = None
    latency_ms: int | None = None
    error: str | None = None
    parser_status: ParserStatus = ParserStatus.NOT_ATTEMPTED
    fallback_reason: FallbackReason | None = None
    prompt_summary: dict[str, Any] = Field(default_factory=dict)
    prompt_hash: str | None = None


class StructuredDecisionResult(BaseModel):
    decision: StructuredDecision
    decision_source: DecisionSource
    parser_status: ParserStatus = ParserStatus.NOT_ATTEMPTED
    fallback_reason: FallbackReason | None = None
    prompt_summary: dict[str, Any] = Field(default_factory=dict)
    prompt_hash: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_latency_ms: int | None = None
    llm_error: str | None = None
