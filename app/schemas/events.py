from uuid import UUID

from pydantic import BaseModel


class EventPayload(BaseModel):
    event_id: UUID
    tick_number: int
    event_type: str
    actor_agent_id: UUID | None = None
    target_agent_id: UUID | None = None
    payload: dict
    created_at: str
