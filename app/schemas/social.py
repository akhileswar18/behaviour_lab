from enum import StrEnum


class SocialAction(StrEnum):
    WARN = "warn"
    COOPERATE = "cooperate"
    AVOID = "avoid"
    PROPOSE = "propose"
    OBSERVE = "observe"
    WAIT = "wait"


class MessageTargetMode(StrEnum):
    DIRECT = "direct"
    BROADCAST = "broadcast"


class MessageIntent(StrEnum):
    PROPOSE = "propose"
    WARN = "warn"
    COOPERATE = "cooperate"
    AVOID = "avoid"
    OBSERVE = "observe"
    WAIT = "wait"


class EmotionalTone(StrEnum):
    SUPPORTIVE = "supportive"
    ASSERTIVE = "assertive"
    GUARDED = "guarded"
    NEUTRAL = "neutral"


class SimulationEventType(StrEnum):
    WORLD_EVENT = "world_event"
    DECISION = "decision"
    MESSAGE = "message"
    RELATIONSHIP_UPDATE = "relationship_update"
    MEMORY_WRITE = "memory_write"
    SYSTEM = "system"
