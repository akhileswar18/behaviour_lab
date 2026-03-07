from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NeedGaugeRead(BaseModel):
    label: str
    value: float
    severity: str


class GoalSummaryRead(BaseModel):
    id: UUID
    goal_type: str
    priority: float
    status: str
    source: str
    target: dict = Field(default_factory=dict)
    updated_at: datetime


class IntentionSummaryRead(BaseModel):
    id: UUID
    current_action_type: str
    status: str
    rationale: str
    target_zone_id: UUID | None = None
    target_resource_id: UUID | None = None
    is_interruptible: bool
    updated_at: datetime


class RelationshipSummaryRead(BaseModel):
    target_agent_id: UUID
    target_agent_name: str
    trust: float
    affinity: float
    stance: str
    influence: float
    last_updated_tick: int


class DecisionTraceRead(BaseModel):
    id: UUID
    tick_number: int
    selected_action: str
    rationale: str
    confidence: float
    persona_factors: dict = Field(default_factory=dict)
    relationship_factors: dict = Field(default_factory=dict)
    world_event_factors: dict = Field(default_factory=dict)
    decision_source: str = "deterministic"
    parser_status: str = "not_attempted"
    fallback_reason: str | None = None
    llm_metadata: dict = Field(default_factory=dict)
    message_id: UUID | None = None
    created_at: datetime


class MemoryInfluenceRead(BaseModel):
    trace_id: UUID
    decision_log_id: UUID
    memory_id: UUID
    tick_number: int
    relevance_score: float
    memory_type: str
    content: str
    salience: float
    valence: float
    created_at: datetime


class InventoryItemRead(BaseModel):
    resource_type: str
    quantity: int


class InteractionMetricsRead(BaseModel):
    messages_sent: int
    messages_received: int
    cooperation_events: int
    conflict_events: int
    goal_completion_rate: float
    interruption_count: int
    completed_goals: int
    fallback_count: int = 0
    llm_decision_count: int = 0
    deterministic_decision_count: int = 0


class AgentSummaryRead(BaseModel):
    id: UUID
    name: str
    persona_label: str
    communication_style: str
    cooperation_tendency: float
    risk_tolerance: float
    memory_sensitivity: float
    emotional_bias: float
    zone_id: UUID | None = None
    zone_name: str | None = None
    mood: str
    inventory: list[InventoryItemRead] = Field(default_factory=list)


class AgentScenarioOptionRead(BaseModel):
    scenario_id: UUID
    scenario_name: str


class AgentIdentityRead(BaseModel):
    identity_key: str
    name: str
    persona_label: str
    scenario_count: int
    latest_agent_id: UUID
    latest_scenario_id: UUID
    latest_scenario_name: str
    latest_zone_name: str | None = None
    latest_mood: str = "neutral"
    available_scenarios: list[AgentScenarioOptionRead] = Field(default_factory=list)


class NeedHistoryPointRead(BaseModel):
    tick_number: int
    hunger: float
    safety_need: float
    social_need: float


class PlanHistoryPointRead(BaseModel):
    tick_number: int
    event_type: str
    summary: str
    status: str | None = None
    action_type: str | None = None


class ActionMixItemRead(BaseModel):
    action: str
    count: int


class MemorySummaryRead(BaseModel):
    memory_id: UUID
    tick_number: int
    memory_type: str
    content: str
    relevance_score: float
    salience: float


class MemoryInfluenceTrendPointRead(BaseModel):
    tick_number: int
    count: int
    avg_relevance: float


class BehavioralTrendPointRead(BaseModel):
    tick_number: int
    action_count: int = 0
    interruption_count: int = 0
    move_count: int = 0
    goal_completion_count: int = 0
    zone_transition_count: int = 0
    distinct_action_count: int = 0


class AgentObservatoryRead(BaseModel):
    scenario_id: UUID | None = None
    mode: str = "scenario"
    scope_label: str = ""
    scope_notes: str | None = None
    selected_scenario_id: UUID | None = None
    available_scenarios: list[AgentScenarioOptionRead] = Field(default_factory=list)
    agent: AgentSummaryRead
    needs: list[NeedGaugeRead] = Field(default_factory=list)
    needs_history: list[NeedHistoryPointRead] = Field(default_factory=list)
    active_goal: GoalSummaryRead | None = None
    active_intention: IntentionSummaryRead | None = None
    recent_goals: list[GoalSummaryRead] = Field(default_factory=list)
    recent_intentions: list[IntentionSummaryRead] = Field(default_factory=list)
    plan_history: list[PlanHistoryPointRead] = Field(default_factory=list)
    decisions: list[DecisionTraceRead] = Field(default_factory=list)
    action_mix: list[ActionMixItemRead] = Field(default_factory=list)
    memory_influences: list[MemoryInfluenceRead] = Field(default_factory=list)
    memory_summary: list[MemorySummaryRead] = Field(default_factory=list)
    memory_influence_trend: list[MemoryInfluenceTrendPointRead] = Field(default_factory=list)
    relationships: list[RelationshipSummaryRead] = Field(default_factory=list)
    interaction_metrics: InteractionMetricsRead
    behavioral_trends: list[BehavioralTrendPointRead] = Field(default_factory=list)
    recent_events: list[dict] = Field(default_factory=list)


class WorldMetricsRead(BaseModel):
    average_trust: float
    goal_completion_rate: float
    movement_frequency: float
    resource_scarcity: float


class SocialEdgeRead(BaseModel):
    source_agent_id: UUID
    target_agent_id: UUID
    source_agent_name: str
    target_agent_name: str
    trust: float
    affinity: float
    stance: str
    influence: float
    last_updated_tick: int


class AgentInteractionMetricRead(BaseModel):
    agent_id: UUID
    agent_name: str
    messages_sent: int
    messages_received: int
    cooperation_events: int
    conflict_events: int
    relationship_updates: int


class RelationshipHistoryRead(BaseModel):
    event_id: UUID
    tick_number: int
    source_agent_id: UUID | None = None
    target_agent_id: UUID | None = None
    source_agent_name: str | None = None
    target_agent_name: str | None = None
    trust_before: float | None = None
    trust_after: float | None = None
    affinity_before: float | None = None
    affinity_after: float | None = None
    stance: str | None = None
    content: str


class CausalChainRead(BaseModel):
    message_event_id: UUID
    relationship_event_id: UUID | None = None
    message_id: UUID | None = None
    tick_number: int
    sender_agent_id: UUID | None = None
    receiver_agent_id: UUID | None = None
    sender_agent_name: str | None = None
    receiver_agent_name: str | None = None
    intent: str | None = None
    emotional_tone: str | None = None
    relationship_delta: dict = Field(default_factory=dict)
    memory_ids: list[UUID] = Field(default_factory=list)


class SocialAnalyticsRead(BaseModel):
    scenario_id: UUID
    communication_feed: list[dict] = Field(default_factory=list)
    relationship_graph: list[SocialEdgeRead] = Field(default_factory=list)
    interaction_metrics: list[AgentInteractionMetricRead] = Field(default_factory=list)
    relationship_history: list[RelationshipHistoryRead] = Field(default_factory=list)
    causal_chains: list[CausalChainRead] = Field(default_factory=list)
    cooperation_conflict_summary: dict = Field(default_factory=dict)


class ZoneOccupancyRead(BaseModel):
    zone_id: UUID
    zone_name: str
    zone_type: str
    occupant_count: int
    occupants: list[dict] = Field(default_factory=list)
    resource_types: list[str] = Field(default_factory=list)


class ResourceDistributionRead(BaseModel):
    resource_id: UUID
    zone_id: UUID
    zone_name: str | None = None
    resource_type: str
    quantity: int
    status: str


class WorldStateSummaryRead(BaseModel):
    zone_count: int
    agent_count: int
    resource_unit_count: int
    active_tick_span: int


class WorldAnalyticsRead(BaseModel):
    scenario_id: UUID
    current_tick: int
    world_state: WorldStateSummaryRead
    global_event_feed: list[dict] = Field(default_factory=list)
    zone_occupancy: list[ZoneOccupancyRead] = Field(default_factory=list)
    resource_distribution: list[ResourceDistributionRead] = Field(default_factory=list)
    metrics: WorldMetricsRead
