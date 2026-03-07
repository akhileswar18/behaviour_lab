from pydantic import BaseModel, Field, field_validator


class PersonaInput(BaseModel):
    label: str
    communication_style: str = "neutral"
    risk_tolerance: float = 0.5
    cooperation_tendency: float = 0.5
    memory_sensitivity: float = 0.5
    emotional_bias: float = 0.0
    priority_weights: dict[str, float] = Field(default_factory=dict)
    reaction_biases: dict[str, float] = Field(default_factory=dict)

    @field_validator("risk_tolerance", "cooperation_tendency", "memory_sensitivity")
    @classmethod
    def clamp_unit_values(cls, value: float) -> float:
        return max(0.0, min(1.0, value))

    @field_validator("emotional_bias")
    @classmethod
    def clamp_emotional_bias(cls, value: float) -> float:
        return max(-1.0, min(1.0, value))


class AgentInitialState(BaseModel):
    mood: str = "neutral"
    goals: list[str] = Field(default_factory=list)
    hunger: float = 0.0
    safety_need: float = 0.0
    social_need: float = 0.0
    zone: str | None = None
    inventory: dict[str, int] = Field(default_factory=dict)


class AgentConfig(BaseModel):
    name: str
    persona: PersonaInput
    initial_state: AgentInitialState = Field(default_factory=AgentInitialState)


class GoalState(BaseModel):
    goal_type: str
    priority: float = 0.5
    status: str = "active"
    target: dict[str, str] = Field(default_factory=dict)
    source: str = "seed"


class IntentionState(BaseModel):
    current_action_type: str = "wait"
    status: str = "active"
    rationale: str = ""
    target_zone_id: str | None = None
    target_resource_id: str | None = None
    is_interruptible: bool = True


class SocialDecision(BaseModel):
    action: str
    intent: str
    emotional_tone: str
    rationale: str
    confidence: float = 0.5
    target_zone_id: str | None = None
    target_resource_id: str | None = None
