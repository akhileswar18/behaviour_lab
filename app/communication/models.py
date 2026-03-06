from pydantic import BaseModel, Field


class MessagePayload(BaseModel):
    sender_agent_id: str
    receiver_agent_id: str | None = None
    target_mode: str = "direct"
    content: str
    intent: str = "observe"
    emotional_tone: str = "neutral"
    intent_tags: list[str] = Field(default_factory=list)
