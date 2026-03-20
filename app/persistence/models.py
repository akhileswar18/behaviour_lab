from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Scenario(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str = ""
    status: str = "ready"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PersonaProfile(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    communication_style: str = "neutral"
    priority_weights: dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON))
    reaction_biases: dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON))
    risk_tolerance: float = 0.5
    cooperation_tendency: float = 0.5
    memory_sensitivity: float = 0.5
    emotional_bias: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Agent(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    persona_profile_id: UUID = Field(index=True)
    name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentStateSnapshot(SQLModel, table=True):
    __table_args__ = (Index("ix_agent_state_agent_tick", "agent_id", "tick_number"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(index=True)
    tick_number: int = Field(default=0, index=True)
    mood: str = "neutral"
    active_goals: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    beliefs: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    energy: float = 100.0
    stress: float = 0.0
    hunger: float = 0.0
    safety_need: float = 0.0
    social_need: float = 0.0
    zone_id: Optional[UUID] = Field(default=None, index=True)
    tile_x: Optional[int] = Field(default=None, index=True)
    tile_y: Optional[int] = Field(default=None, index=True)
    inventory: dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TileMapConfig(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("scenario_id", name="uq_tilemapconfig_scenario"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    map_file_path: str
    tile_width: int = 16
    tile_height: int = 16
    grid_width: int = 0
    grid_height: int = 0
    zone_bindings: dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Goal(SQLModel, table=True):
    __table_args__ = (Index("ix_goal_scenario_agent_status", "scenario_id", "agent_id", "status"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    agent_id: UUID = Field(index=True)
    goal_type: str
    priority: float = 0.5
    status: str = "active"
    target: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    source: str = "scenario_seed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Intention(SQLModel, table=True):
    __table_args__ = (Index("ix_intention_scenario_agent_status", "scenario_id", "agent_id", "status"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    agent_id: UUID = Field(index=True)
    goal_id: Optional[UUID] = Field(default=None, index=True)
    current_action_type: str = "wait"
    status: str = "active"
    rationale: str = ""
    target_zone_id: Optional[UUID] = Field(default=None, index=True)
    target_resource_id: Optional[UUID] = Field(default=None, index=True)
    is_interruptible: bool = True
    started_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Zone(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("scenario_id", "name", name="uq_zone_scenario_name"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    name: str
    zone_type: str = "commons"
    zone_metadata: dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Resource(SQLModel, table=True):
    __table_args__ = (Index("ix_resource_scenario_zone_type", "scenario_id", "zone_id", "resource_type"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    zone_id: UUID = Field(index=True)
    resource_type: str
    quantity: int = 0
    status: str = "available"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Memory(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(index=True)
    source_event_id: Optional[UUID] = None
    memory_type: str = "observation"
    content: str
    salience: float = 0.5
    valence: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MemoryRetrievalTrace(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(index=True)
    tick_number: int = Field(default=0, index=True)
    decision_log_id: UUID
    memory_id: UUID
    relevance_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    __table_args__ = (
        Index("ix_message_scenario_tick", "scenario_id", "tick_number"),
        Index("ix_message_sender_receiver", "sender_agent_id", "receiver_agent_id"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    tick_number: int = Field(default=0, index=True)
    sender_agent_id: UUID = Field(index=True)
    receiver_agent_id: Optional[UUID] = Field(default=None, index=True)
    target_mode: str = "direct"
    message_type: str = "direct"
    content: str
    intent: str = "observe"
    emotional_tone: str = "neutral"
    intent_tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Relationship(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "scenario_id",
            "source_agent_id",
            "target_agent_id",
            name="uq_relationship_scenario_pair",
        ),
        Index("ix_relationship_scenario_agents", "scenario_id", "source_agent_id", "target_agent_id"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    source_agent_id: UUID = Field(index=True)
    target_agent_id: UUID = Field(index=True)
    trust: float = 0.0
    affinity: float = 0.0
    stance: str = "neutral"
    influence: float = 0.5
    last_updated_tick: int = Field(default=0, index=True)
    last_interaction_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SimulationEvent(SQLModel, table=True):
    __table_args__ = (
        Index("ix_event_scenario_tick_type", "scenario_id", "tick_number", "event_type"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    tick_number: int = Field(default=0, index=True)
    event_type: str = "system"
    actor_agent_id: Optional[UUID] = Field(default=None, index=True)
    target_agent_id: Optional[UUID] = Field(default=None, index=True)
    content: str = ""
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionLog(SQLModel, table=True):
    __table_args__ = (
        Index("ix_decision_scenario_tick_agent", "scenario_id", "tick_number", "agent_id"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    agent_id: UUID = Field(index=True)
    tick_number: int = Field(default=0, index=True)
    observed_event_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    selected_action: str = "idle"
    rationale: str = ""
    confidence: float = 0.5
    persona_factors: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    relationship_factors: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    world_event_factors: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    decision_source: str = "deterministic"
    parser_status: str = "not_attempted"
    fallback_reason: Optional[str] = None
    prompt_summary: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    llm_metadata: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    message_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScenarioEventInjection(SQLModel, table=True):
    __table_args__ = (
        Index("ix_event_injection_scenario_tick", "scenario_id", "tick_number", "is_consumed"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    tick_number: int = Field(default=0, index=True)
    event_key: str
    event_content: str
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    is_consumed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TickResult(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    tick_number: int = Field(default=0, index=True)
    status: str = "completed"
    processed_agents: int = 0
    events_created: int = 0
    messages_created: int = 0
    duration_ms: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RunMetadata(SQLModel, table=True):
    __table_args__ = (Index("ix_run_metadata_scenario", "scenario_id", "created_at"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(index=True)
    source_scenario_id: Optional[UUID] = None
    run_kind: str = "baseline"
    variant_name: str = "baseline"
    persona_overrides: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    planning_overrides: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    world_overrides: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    policy_mode: str = "deterministic"
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_config_summary: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    decision_source_counts: dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))
    fallback_count: int = 0
    parse_failure_count: int = 0
    ticks_requested: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


class RunComparisonSummary(SQLModel, table=True):
    __table_args__ = (Index("ix_run_comparison_pair", "base_run_id", "variant_run_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    base_run_id: UUID = Field(index=True)
    variant_run_id: UUID = Field(index=True)
    base_scenario_id: UUID = Field(index=True)
    variant_scenario_id: UUID = Field(index=True)
    decision_count_delta: int = 0
    message_count_delta: int = 0
    relationship_avg_trust_delta: float = 0.0
    completed_goal_delta: int = 0
    move_event_delta: int = 0
    resource_event_delta: int = 0
    fallback_count_delta: int = 0
    llm_decision_delta: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
