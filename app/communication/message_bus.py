from datetime import datetime
from uuid import UUID

from app.persistence.models import Message
from app.schemas.social import MessageIntent, MessageTargetMode, EmotionalTone


def build_message(
    scenario_id: UUID,
    tick_number: int,
    sender_agent_id: UUID,
    receiver_agent_id: UUID | None,
    content: str,
    intent: str | MessageIntent = MessageIntent.OBSERVE,
    emotional_tone: str | EmotionalTone = EmotionalTone.NEUTRAL,
    target_mode: str | MessageTargetMode = MessageTargetMode.DIRECT,
    intent_tags: list[str] | None = None,
) -> Message:
    tags = intent_tags or []
    return Message(
        scenario_id=scenario_id,
        tick_number=tick_number,
        sender_agent_id=sender_agent_id,
        receiver_agent_id=receiver_agent_id,
        target_mode=str(target_mode),
        message_type=str(target_mode),
        content=content,
        intent=str(intent),
        emotional_tone=str(emotional_tone),
        intent_tags=tags,
        created_at=datetime.utcnow(),
    )
