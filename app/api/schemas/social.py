from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MessageRead(BaseModel):
    id: UUID
    scenario_id: UUID
    tick_number: int
    sender_agent_id: UUID
    receiver_agent_id: UUID | None = None
    target_mode: str
    content: str
    intent: str
    emotional_tone: str
    intent_tags: list[str] = Field(default_factory=list)
    created_at: datetime


class RelationshipRead(BaseModel):
    source_agent_id: UUID
    target_agent_id: UUID
    trust: float
    affinity: float
    stance: str
    influence: float
    last_updated_tick: int
    last_interaction_at: datetime | None = None
    updated_at: datetime


class GoalRead(BaseModel):
    id: UUID
    scenario_id: UUID
    agent_id: UUID
    goal_type: str
    priority: float
    status: str
    target: dict = Field(default_factory=dict)
    source: str
    created_at: datetime
    updated_at: datetime


class IntentionRead(BaseModel):
    id: UUID
    scenario_id: UUID
    agent_id: UUID
    goal_id: UUID | None = None
    current_action_type: str
    status: str
    rationale: str
    target_zone_id: UUID | None = None
    target_resource_id: UUID | None = None
    is_interruptible: bool
    started_at: datetime
    updated_at: datetime


class ZoneRead(BaseModel):
    id: UUID
    scenario_id: UUID
    name: str
    zone_type: str
    metadata: dict = Field(default_factory=dict)
    occupant_ids: list[UUID] = Field(default_factory=list)
    occupant_names: list[str] = Field(default_factory=list)
    occupant_count: int = 0
    resource_types: list[str] = Field(default_factory=list)
    resource_count: int = 0


class ResourceRead(BaseModel):
    id: UUID
    scenario_id: UUID
    zone_id: UUID
    zone_name: str | None = None
    resource_type: str
    quantity: int
    status: str
    created_at: datetime
    updated_at: datetime


class TimelineEventRead(BaseModel):
    id: UUID
    tick_number: int
    event_type: str
    actor_agent_id: UUID | None = None
    target_agent_id: UUID | None = None
    content: str
    payload: dict = Field(default_factory=dict)
    created_at: datetime
