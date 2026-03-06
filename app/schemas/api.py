from uuid import UUID

from pydantic import BaseModel, Field


class ScenarioCreate(BaseModel):
    name: str
    description: str = ""
    max_ticks: int | None = Field(default=None, ge=1)


class ScenarioRead(BaseModel):
    id: UUID
    name: str
    status: str
    current_tick: int = 0


class RunRequest(BaseModel):
    ticks: int = Field(default=1, ge=1)


class TickResultRead(BaseModel):
    tick_number: int
    status: str
    processed_agents: int
    events_created: int
    messages_created: int
    duration_ms: int


class RunResponse(BaseModel):
    scenario_id: UUID
    start_tick: int
    end_tick: int
    tick_results: list[TickResultRead]


class CompareRerunRequest(BaseModel):
    ticks: int = Field(default=3, ge=1)
    variant_name: str = "persona-variant"
    persona_overrides: dict[str, dict[str, float | str]] = Field(default_factory=dict)


class CompareDiff(BaseModel):
    decision_count_delta: int
    message_count_delta: int
    relationship_avg_trust_delta: float


class CompareRerunResponse(BaseModel):
    base_scenario_id: UUID
    variant_scenario_id: UUID
    comparison: dict


class AgentRead(BaseModel):
    id: UUID
    scenario_id: UUID
    name: str
    persona_label: str
    mood: str = "neutral"
    active_goals: list[str] = Field(default_factory=list)


class RelationshipRead(BaseModel):
    source_agent_id: UUID
    target_agent_id: UUID
    trust: float
    affinity: float
    influence: float
    last_updated_tick: int
