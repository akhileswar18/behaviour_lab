from datetime import datetime

from app.persistence.models import Memory


def create_memory(agent_id, source_event_id, memory_type: str, content: str, salience: float = 0.5, valence: float = 0.0) -> Memory:
    return Memory(
        agent_id=agent_id,
        source_event_id=source_event_id,
        memory_type=memory_type,
        content=content,
        salience=salience,
        valence=valence,
        created_at=datetime.utcnow(),
    )


def create_social_memory(
    agent_id,
    source_event_id,
    intent: str,
    emotional_tone: str,
    content: str,
) -> Memory:
    base_salience = 0.6 if intent in {"warn", "propose", "cooperate"} else 0.45
    valence = 0.15 if emotional_tone in {"supportive", "neutral"} else -0.1
    return create_memory(
        agent_id=agent_id,
        source_event_id=source_event_id,
        memory_type="social_effect",
        content=content,
        salience=base_salience,
        valence=valence,
    )
