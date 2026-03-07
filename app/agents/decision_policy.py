from __future__ import annotations

from app.agents.models import AgentConfig, SocialDecision
from app.schemas.decision_engine import DecisionContext, StructuredDecision
from app.schemas.social import SocialAction


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


def _decide(
    agent: AgentConfig,
    observed_events: list[dict],
    tick_number: int,
    relationship_context: dict | None = None,
    needs_context: dict | None = None,
    planning_context: dict | None = None,
) -> StructuredDecision:
    relationship_context = relationship_context or {}
    needs_context = needs_context or {}
    planning_context = planning_context or {}
    relationship_affinity = float(relationship_context.get("affinity", 0.0))
    relationship_trust = float(relationship_context.get("trust", 0.0))
    hunger = float(needs_context.get("hunger", 0.0))
    safety_need = float(needs_context.get("safety_need", 0.0))
    social_need = float(needs_context.get("social_need", 0.0))

    planned_action = planning_context.get("action")
    if planned_action in {
        SocialAction.MOVE.value,
        SocialAction.ACQUIRE_RESOURCE.value,
        SocialAction.CONSUME_RESOURCE.value,
    }:
        return StructuredDecision(
            action=planned_action,
            intent=planned_action,
            emotional_tone="urgent" if safety_need >= 0.8 or hunger >= 0.8 else "neutral",
            rationale=str(planning_context.get("rationale", "Plan-driven action selected.")),
            confidence=0.9,
            target_zone_id=(
                str(planning_context.get("target_zone_id"))
                if planning_context.get("target_zone_id")
                else None
            ),
            target_resource_id=(
                str(planning_context.get("target_resource_id"))
                if planning_context.get("target_resource_id")
                else None
            ),
        )

    style = agent.persona.communication_style.lower()
    coop = agent.persona.cooperation_tendency
    risk = agent.persona.risk_tolerance
    memory_weight = agent.persona.memory_sensitivity
    world_pressure = _world_pressure(observed_events)

    if safety_need > 0.7 or (style == "direct" and (risk > 0.6 or world_pressure > 0.3)):
        return StructuredDecision(
            action=SocialAction.WARN.value,
            intent="warn",
            emotional_tone="assertive",
            rationale=(
                f"{agent.name} warns peers due to safety={safety_need:.2f}, "
                f"risk={risk:.2f}, pressure={world_pressure:.2f}."
            ),
            confidence=0.84,
        )

    cooperative_score = (
        coop + (relationship_affinity * 0.3) + (relationship_trust * 0.2) + (social_need * 0.2)
    )
    if style == "diplomatic" and cooperative_score >= 0.55:
        return StructuredDecision(
            action=SocialAction.COOPERATE.value,
            intent="propose",
            emotional_tone="supportive",
            rationale=(
                f"{agent.name} cooperates with score={cooperative_score:.2f} while "
                f"pursuing {planning_context.get('goal_type', 'context')}."
            ),
            confidence=0.8,
        )

    if style == "reserved" and (risk < 0.45 or world_pressure > 0.4):
        return StructuredDecision(
            action=SocialAction.AVOID.value,
            intent="avoid",
            emotional_tone="guarded",
            rationale=f"{agent.name} avoids escalation with risk={risk:.2f} and pressure={world_pressure:.2f}.",
            confidence=0.77,
        )

    if memory_weight > 0.7 and relationship_trust >= 0:
        return StructuredDecision(
            action=SocialAction.PROPOSE.value,
            intent="propose",
            emotional_tone="neutral",
            rationale=f"{agent.name} proposes a plan using memory sensitivity={memory_weight:.2f}.",
            confidence=0.72,
        )

    if not observed_events and tick_number % 2 == 0:
        return StructuredDecision(
            action=SocialAction.OBSERVE.value,
            intent="observe",
            emotional_tone="neutral",
            rationale=f"{agent.name} has no recent events and keeps observing at tick {tick_number}.",
            confidence=0.6,
        )

    return StructuredDecision(
        action=SocialAction.WAIT.value,
        intent="wait",
        emotional_tone="neutral",
        rationale=f"{agent.name} waits to collect more signal at tick {tick_number}.",
        confidence=0.65,
    )


def choose_structured_action(context: DecisionContext) -> StructuredDecision:
    persona_payload = {
        "label": context.persona.get("label", "default"),
        "communication_style": context.persona.get("communication_style", "neutral"),
        "risk_tolerance": context.persona.get("risk_tolerance", 0.5),
        "cooperation_tendency": context.persona.get("cooperation_tendency", 0.5),
        "memory_sensitivity": context.persona.get("memory_sensitivity", 0.5),
        "emotional_bias": context.persona.get("emotional_bias", 0.0),
    }
    state_payload = {
        "mood": context.mood,
        "goals": [context.active_goal.get("goal_type")] if context.active_goal else [],
        "hunger": float(context.needs.get("hunger", 0.0)),
        "safety_need": float(context.needs.get("safety_need", 0.0)),
        "social_need": float(context.needs.get("social_need", 0.0)),
        "inventory": context.zone.get("inventory", {}) if context.zone else {},
    }
    agent = AgentConfig(name=context.agent_name, persona=persona_payload, initial_state=state_payload)
    relationship_context = context.relationships[0] if context.relationships else {}
    return _decide(
        agent=agent,
        observed_events=context.observed_events,
        tick_number=context.tick_number,
        relationship_context=relationship_context,
        needs_context=context.needs,
        planning_context=context.planning_context,
    )


def choose_action(
    agent: AgentConfig,
    observed_events: list[dict],
    tick_number: int,
    relationship_context: dict | None = None,
    needs_context: dict | None = None,
    planning_context: dict | None = None,
) -> SocialDecision:
    decision = _decide(
        agent=agent,
        observed_events=observed_events,
        tick_number=tick_number,
        relationship_context=relationship_context,
        needs_context=needs_context,
        planning_context=planning_context,
    )
    return SocialDecision(**decision.model_dump())
