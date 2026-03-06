from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import Session

from app.agents.decision_policy import choose_action
from app.agents.models import AgentConfig
from app.agents.relationship_policy import compute_relationship_delta, derive_stance
from app.communication.handlers import emit_agent_message
from app.memory.retriever import retrieve_relevant
from app.memory.summarizer import score_salience
from app.memory.writer import create_memory
from app.persistence.models import (
    AgentStateSnapshot,
    DecisionLog,
    MemoryRetrievalTrace,
    PersonaProfile,
    SimulationEvent,
    TickResult,
)
from app.persistence.repositories.agent_repository import AgentRepository
from app.persistence.repositories.memory_repository import MemoryRepository
from app.persistence.repositories.social_repository import SocialRepository
from app.schemas.social import SimulationEventType
from app.simulation.world_state import build_tick_context, mark_world_events_consumed


def _build_agent_config(agent_name: str, persona: PersonaProfile | None, latest_state: AgentStateSnapshot | None) -> AgentConfig:
    persona_payload = {
        "label": persona.label if persona else "default",
        "communication_style": persona.communication_style if persona else "neutral",
        "risk_tolerance": persona.risk_tolerance if persona else 0.5,
        "cooperation_tendency": persona.cooperation_tendency if persona else 0.5,
        "memory_sensitivity": persona.memory_sensitivity if persona else 0.5,
        "emotional_bias": persona.emotional_bias if persona else 0.0,
    }
    state_payload = {
        "mood": latest_state.mood if latest_state else "neutral",
        "goals": latest_state.active_goals if latest_state else [],
    }
    return AgentConfig(name=agent_name, persona=persona_payload, initial_state=state_payload)


def _pick_receiver(agent_id: UUID, peers: list) -> UUID | None:
    for peer in peers:
        if peer.id != agent_id:
            return peer.id
    return None


def run_tick(session: Session, scenario_id: UUID, tick_number: int) -> TickResult:
    agent_repo = AgentRepository(session)
    memory_repo = MemoryRepository(session)
    social_repo = SocialRepository(session)

    context = build_tick_context(session, scenario_id, tick_number)
    agents = context["agents"]
    recent_events = context["events"]
    world_events = context["world_events"]

    processed_agents = 0
    events_created = 0
    messages_created = 0

    world_event_observed: list[dict] = []
    for world_event in world_events:
        stored_event = social_repo.add_event(
            SimulationEvent(
                scenario_id=scenario_id,
                tick_number=tick_number,
                event_type=SimulationEventType.WORLD_EVENT.value,
                content=world_event.event_content,
                payload={
                    "world_event_id": str(world_event.id),
                    "event_key": world_event.event_key,
                    **(world_event.payload or {}),
                },
                created_at=datetime.utcnow(),
            )
        )
        events_created += 1
        world_event_observed.append(
            {
                "event_type": stored_event.event_type,
                "content": stored_event.content,
                "payload": stored_event.payload,
            }
        )
    mark_world_events_consumed(session, world_events)

    for agent in agents:
        processed_agents += 1
        persona = session.get(PersonaProfile, agent.persona_profile_id)
        latest_state = agent_repo.latest_state(agent.id)
        agent_cfg = _build_agent_config(agent.name, persona, latest_state)
        observed_events = [
            {"event_type": event.event_type, "content": event.content, "payload": event.payload}
            for event in recent_events
        ] + world_event_observed
        recalled = retrieve_relevant(session, agent.id, limit=3)
        relationships = social_repo.list_relationships(scenario_id, agent.id)
        outbound_relationship = next(
            (r for r in relationships if r.source_agent_id == agent.id),
            None,
        )
        relationship_context = {
            "trust": outbound_relationship.trust if outbound_relationship else 0.0,
            "affinity": outbound_relationship.affinity if outbound_relationship else 0.0,
        }
        decision = choose_action(
            agent_cfg,
            observed_events,
            tick_number=tick_number,
            relationship_context=relationship_context,
        )

        decision_log = DecisionLog(
            scenario_id=scenario_id,
            agent_id=agent.id,
            tick_number=tick_number,
            observed_event_ids=[
                str(item.get("payload", {}).get("world_event_id", ""))
                for item in observed_events
                if item.get("payload", {}).get("world_event_id")
            ],
            selected_action=decision.action,
            rationale=decision.rationale,
            confidence=decision.confidence,
            persona_factors={
                "communication_style": agent_cfg.persona.communication_style,
                "cooperation_tendency": agent_cfg.persona.cooperation_tendency,
                "risk_tolerance": agent_cfg.persona.risk_tolerance,
                "memory_sensitivity": agent_cfg.persona.memory_sensitivity,
            },
            relationship_factors=relationship_context,
            world_event_factors={"world_event_count": len(world_event_observed)},
            created_at=datetime.utcnow(),
        )
        session.add(decision_log)
        session.commit()
        session.refresh(decision_log)

        for memory in recalled:
            session.add(
                MemoryRetrievalTrace(
                    agent_id=agent.id,
                    tick_number=tick_number,
                    decision_log_id=decision_log.id,
                    memory_id=memory.id,
                    relevance_score=0.8,
                    created_at=datetime.utcnow(),
                )
            )

        decision_event = social_repo.add_event(
            SimulationEvent(
                scenario_id=scenario_id,
                tick_number=tick_number,
                event_type=SimulationEventType.DECISION.value,
                actor_agent_id=agent.id,
                content=decision.rationale,
                payload={
                    "decision_id": str(decision_log.id),
                    "action": decision.action,
                    "intent": decision.intent,
                    "emotional_tone": decision.emotional_tone,
                },
                created_at=datetime.utcnow(),
            )
        )
        events_created += 1

        memory_repo.add_memory(
            create_memory(
                agent_id=agent.id,
                source_event_id=decision_event.id,
                memory_type="decision",
                content=decision.rationale,
                salience=score_salience(0.55, SimulationEventType.DECISION.value),
                valence=agent_cfg.persona.emotional_bias,
            )
        )

        peers = [candidate for candidate in agents if candidate.id != agent.id]
        receiver_id = _pick_receiver(agent.id, peers)
        if receiver_id is not None:
            message_content = (
                f"{agent.name} {decision.action}s with {decision.emotional_tone} tone: "
                f"{decision.rationale}"
            )
            message, message_event = emit_agent_message(
                session=session,
                scenario_id=scenario_id,
                tick_number=tick_number,
                sender_agent_id=agent.id,
                receiver_agent_id=receiver_id,
                content=message_content,
                intent=decision.intent,
                emotional_tone=decision.emotional_tone,
                decision_log_id=decision_log.id,
            )
            messages_created += 1
            events_created += 1

            decision_log.message_id = message.id
            session.add(decision_log)

            trust_delta, affinity_delta = compute_relationship_delta(
                decision.intent,
                decision.emotional_tone,
            )
            previous_trust = outbound_relationship.trust if outbound_relationship else 0.0
            previous_affinity = outbound_relationship.affinity if outbound_relationship else 0.0
            relationship = social_repo.upsert_relationship(
                scenario_id=scenario_id,
                source_agent_id=agent.id,
                target_agent_id=receiver_id,
                trust_delta=trust_delta,
                affinity_delta=affinity_delta,
                stance=derive_stance(previous_trust + trust_delta, previous_affinity + affinity_delta),
                tick_number=tick_number,
            )
            relationship_event = social_repo.add_event(
                SimulationEvent(
                    scenario_id=scenario_id,
                    tick_number=tick_number,
                    event_type=SimulationEventType.RELATIONSHIP_UPDATE.value,
                    actor_agent_id=agent.id,
                    target_agent_id=receiver_id,
                    content=f"Relationship update from {decision.intent}/{decision.emotional_tone}",
                    payload={
                        "decision_id": str(decision_log.id),
                        "message_id": str(message.id),
                        "relationship_id": str(relationship.id),
                        "trust_before": previous_trust,
                        "trust_after": relationship.trust,
                        "affinity_before": previous_affinity,
                        "affinity_after": relationship.affinity,
                        "stance": relationship.stance,
                    },
                    created_at=datetime.utcnow(),
                )
            )
            events_created += 1

            memory_repo.add_memory(
                create_memory(
                    agent_id=agent.id,
                    source_event_id=message_event.id,
                    memory_type="message",
                    content=f"Sent: {message.content}",
                    salience=score_salience(0.5, SimulationEventType.MESSAGE.value),
                    valence=0.1 if trust_delta >= 0 else -0.1,
                )
            )
            memory_repo.add_memory(
                create_memory(
                    agent_id=receiver_id,
                    source_event_id=relationship_event.id,
                    memory_type="social_effect",
                    content=f"Received message from {agent.name}: {message.intent}",
                    salience=score_salience(0.6, SimulationEventType.RELATIONSHIP_UPDATE.value),
                    valence=0.1 if affinity_delta >= 0 else -0.1,
                )
            )

        next_mood = {
            "warn": "alert",
            "cooperate": "engaged",
            "avoid": "guarded",
            "propose": "focused",
            "observe": "curious",
            "wait": "neutral",
        }.get(decision.action, "neutral")
        next_goals = latest_state.active_goals if latest_state else []
        session.add(
            AgentStateSnapshot(
                agent_id=agent.id,
                tick_number=tick_number,
                mood=next_mood,
                active_goals=next_goals,
                beliefs=latest_state.beliefs if latest_state else {},
                energy=max((latest_state.energy if latest_state else 100.0) - 1.0, 0.0),
                stress=min((latest_state.stress if latest_state else 0.0) + 0.4, 100.0),
                created_at=datetime.utcnow(),
            )
        )
        session.commit()

    tick_result = TickResult(
        scenario_id=scenario_id,
        tick_number=tick_number,
        status="completed",
        processed_agents=processed_agents,
        events_created=events_created,
        messages_created=messages_created,
        duration_ms=1,
    )
    session.add(tick_result)
    session.commit()
    session.refresh(tick_result)
    return tick_result
