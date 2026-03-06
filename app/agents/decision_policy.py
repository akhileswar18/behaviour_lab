from app.agents.models import AgentConfig, SocialDecision


def _world_pressure(observed_events: list[dict]) -> float:
    pressure = 0.0
    for event in observed_events:
        payload = event.get("payload", {}) or {}
        valence = payload.get("valence", "neutral")
        urgency = float(payload.get("urgency", 0.0))
        if valence == "negative":
            pressure += urgency * 0.6
        elif valence == "positive":
            pressure -= urgency * 0.4
    return pressure


def choose_action(
    agent: AgentConfig,
    observed_events: list[dict],
    tick_number: int,
    relationship_context: dict | None = None,
) -> SocialDecision:
    relationship_context = relationship_context or {}
    relationship_affinity = float(relationship_context.get("affinity", 0.0))
    relationship_trust = float(relationship_context.get("trust", 0.0))

    style = agent.persona.communication_style.lower()
    coop = agent.persona.cooperation_tendency
    risk = agent.persona.risk_tolerance
    memory_weight = agent.persona.memory_sensitivity
    world_pressure = _world_pressure(observed_events)

    if not observed_events and tick_number % 2 == 0:
        return SocialDecision(
            action="observe",
            intent="observe",
            emotional_tone="neutral",
            rationale=f"{agent.name} has no recent events and keeps observing at tick {tick_number}.",
            confidence=0.6,
        )

    if style == "direct" and (risk > 0.6 or world_pressure > 0.3):
        return SocialDecision(
            action="warn",
            intent="warn",
            emotional_tone="assertive",
            rationale=f"{agent.name} warns peers due to risk={risk:.2f}, pressure={world_pressure:.2f}.",
            confidence=0.84,
        )

    cooperative_score = coop + (relationship_affinity * 0.3) + (relationship_trust * 0.2)
    if style == "diplomatic" and cooperative_score >= 0.55:
        return SocialDecision(
            action="cooperate",
            intent="propose",
            emotional_tone="supportive",
            rationale=f"{agent.name} cooperates with score={cooperative_score:.2f}.",
            confidence=0.8,
        )

    if style == "reserved" and (risk < 0.45 or world_pressure > 0.4):
        return SocialDecision(
            action="avoid",
            intent="avoid",
            emotional_tone="guarded",
            rationale=f"{agent.name} avoids direct escalation with risk={risk:.2f}.",
            confidence=0.77,
        )

    if memory_weight > 0.7 and relationship_trust > 0:
        return SocialDecision(
            action="propose",
            intent="propose",
            emotional_tone="neutral",
            rationale=f"{agent.name} proposes plan using memory sensitivity={memory_weight:.2f}.",
            confidence=0.72,
        )

    return SocialDecision(
        action="wait",
        intent="wait",
        emotional_tone="neutral",
        rationale=f"{agent.name} waits to collect more signal at tick {tick_number}.",
        confidence=0.65,
    )
