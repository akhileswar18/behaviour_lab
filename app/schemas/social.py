from enum import StrEnum


class SocialAction(StrEnum):
    MOVE = "move"
    ACQUIRE_RESOURCE = "acquire_resource"
    CONSUME_RESOURCE = "consume_resource"
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
    URGENT = "urgent"


class GoalStatus(StrEnum):
    ACTIVE = "active"
    DEFERRED = "deferred"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"


class IntentionStatus(StrEnum):
    ACTIVE = "active"
    DEFERRED = "deferred"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"


class ResourceStatus(StrEnum):
    AVAILABLE = "available"
    LOW = "low"
    DEPLETED = "depleted"
    RESERVED = "reserved"


class ZoneType(StrEnum):
    COMMONS = "commons"
    STORAGE = "storage"
    SHELTER = "shelter"
    LOOKOUT = "lookout"
    CLINIC = "clinic"


class SimulationEventType(StrEnum):
    WORLD_EVENT = "world_event"
    DECISION = "decision"
    MESSAGE = "message"
    RELATIONSHIP_UPDATE = "relationship_update"
    MEMORY_WRITE = "memory_write"
    PLAN_CHANGE = "plan_change"
    INTERRUPTION = "interruption"
    MOVE = "move"
    ACQUIRE = "acquire"
    CONSUME = "consume"
    RESOURCE_SHORTAGE = "resource_shortage"
    NEED_THRESHOLD = "need_threshold"
    SYSTEM = "system"


ALLOWED_SOCIAL_ACTIONS = tuple(action.value for action in SocialAction)
ALLOWED_MESSAGE_INTENTS = tuple(intent.value for intent in MessageIntent) + (
    SocialAction.MOVE.value,
    SocialAction.ACQUIRE_RESOURCE.value,
    SocialAction.CONSUME_RESOURCE.value,
)
ALLOWED_EMOTIONAL_TONES = tuple(tone.value for tone in EmotionalTone)
