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


class TimelineEventRead(BaseModel):
    id: UUID
    tick_number: int
    event_type: str
    actor_agent_id: UUID | None = None
    target_agent_id: UUID | None = None
    content: str
    payload: dict = Field(default_factory=dict)
    created_at: datetime
