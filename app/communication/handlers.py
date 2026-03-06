from datetime import datetime
from uuid import UUID

from sqlmodel import Session

from app.communication.message_bus import build_message
from app.persistence.models import SimulationEvent
from app.persistence.repositories.social_repository import SocialRepository
from app.schemas.social import SimulationEventType


def emit_agent_message(
    session: Session,
    scenario_id: UUID,
    tick_number: int,
    sender_agent_id: UUID,
    receiver_agent_id: UUID | None,
    content: str,
    intent: str = "observe",
    emotional_tone: str = "neutral",
    decision_log_id: UUID | None = None,
) -> tuple:
    repo = SocialRepository(session)
    msg = build_message(
        scenario_id=scenario_id,
        tick_number=tick_number,
        sender_agent_id=sender_agent_id,
        receiver_agent_id=receiver_agent_id,
        content=content,
        intent=intent,
        emotional_tone=emotional_tone,
        intent_tags=["social", intent],
    )
    message = repo.create_message(msg)
    event = repo.add_event(
        SimulationEvent(
            scenario_id=scenario_id,
            tick_number=tick_number,
            event_type=SimulationEventType.MESSAGE.value,
            actor_agent_id=sender_agent_id,
            target_agent_id=receiver_agent_id,
            content=content,
            payload={
                "message_id": str(message.id),
                "decision_log_id": str(decision_log_id) if decision_log_id else None,
                "intent": message.intent,
                "emotional_tone": message.emotional_tone,
            },
            created_at=datetime.utcnow(),
        ),
    )
    return message, event
