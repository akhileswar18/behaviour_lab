from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.decision_engine import PolicyMode


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
    policy_mode: PolicyMode | None = None
    llm_config: dict[str, str | float | int | bool | None] = Field(default_factory=dict)


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
    policy_mode: str = PolicyMode.DETERMINISTIC.value
    fallback_count: int = 0
    llm_decision_count: int = 0
    deterministic_decision_count: int = 0
    tick_results: list[TickResultRead]


class CompareRerunRequest(BaseModel):
    ticks: int = Field(default=3, ge=1)
    variant_name: str = "persona-variant"
    persona_overrides: dict[str, dict[str, float | str]] = Field(default_factory=dict)
    planning_overrides: dict[str, dict[str, float | str | int]] = Field(default_factory=dict)
    world_overrides: dict[str, dict[str, float | str | int]] = Field(default_factory=dict)
    base_policy_mode: PolicyMode = PolicyMode.DETERMINISTIC
    variant_policy_mode: PolicyMode = PolicyMode.DETERMINISTIC
    base_llm_config: dict[str, str | float | int | bool | None] = Field(default_factory=dict)
    variant_llm_config: dict[str, str | float | int | bool | None] = Field(default_factory=dict)


class CompareDiff(BaseModel):
    decision_count_delta: int
    message_count_delta: int
    relationship_avg_trust_delta: float
    completed_goal_delta: int = 0
    move_event_delta: int = 0
    resource_event_delta: int = 0


class CompareRerunResponse(BaseModel):
    base_scenario_id: UUID
    variant_scenario_id: UUID
    base_policy_mode: str = PolicyMode.DETERMINISTIC.value
    variant_policy_mode: str = PolicyMode.DETERMINISTIC.value
    comparison: dict


class AgentRead(BaseModel):
    id: UUID
    scenario_id: UUID
    name: str
    persona_label: str
    mood: str = "neutral"
    active_goals: list[str] = Field(default_factory=list)
    hunger: float = 0.0
    safety_need: float = 0.0
    social_need: float = 0.0
    zone_id: UUID | None = None
    zone_name: str | None = None
    inventory: dict[str, int] = Field(default_factory=dict)
    active_goal: str | None = None
    active_intention: str | None = None


class RelationshipRead(BaseModel):
    source_agent_id: UUID
    target_agent_id: UUID
    trust: float
    affinity: float
    influence: float
    last_updated_tick: int
