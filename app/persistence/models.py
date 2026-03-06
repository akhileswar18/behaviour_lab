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
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(index=True)
    tick_number: int = Field(default=0, index=True)
    mood: str = "neutral"
    active_goals: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    beliefs: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    energy: float = 100.0
    stress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


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
    ticks_requested: int = 0
    persona_overrides: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
