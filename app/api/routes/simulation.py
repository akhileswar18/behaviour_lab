from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_session
from app.persistence.models import (
    Agent,
    AgentStateSnapshot,
    DecisionLog,
    Message,
    PersonaProfile,
    Relationship,
    RunComparisonSummary,
    RunMetadata,
    Scenario,
    ScenarioEventInjection,
    SimulationEvent,
)
from app.persistence.repositories.social_repository import SocialRepository
from app.persistence.repositories.scenario_repository import ScenarioRepository
from app.schemas.api import CompareRerunRequest, CompareRerunResponse, RunRequest, RunResponse, TickResultRead
from app.schemas.social import SimulationEventType
from app.simulation.runner import SimulationRunner
from app.simulation.scenario_loader import build_variant_name, merge_persona_overrides

router = APIRouter(prefix="/scenarios", tags=["simulation"])


@router.post("/{scenario_id}/run", response_model=RunResponse)
def run_scenario(scenario_id: UUID, request: RunRequest, session: Session = Depends(get_session)) -> RunResponse:
    scenario_repo = ScenarioRepository(session)
    scenario = scenario_repo.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario_repo.update_status(scenario_id, "running")
    runner = SimulationRunner(session)
    rows = runner.run(scenario_id, request.ticks)
    tick_results = [
        TickResultRead(
            tick_number=row.tick_number,
            status=row.status,
            processed_agents=row.processed_agents,
            events_created=row.events_created,
            messages_created=row.messages_created,
            duration_ms=row.duration_ms,
        )
        for row in rows
    ]

    scenario_repo.update_status(scenario_id, "paused")
    return RunResponse(
        scenario_id=scenario_id,
        start_tick=tick_results[0].tick_number if tick_results else 0,
        end_tick=tick_results[-1].tick_number if tick_results else 0,
        tick_results=tick_results,
    )


@router.post("/{scenario_id}/reset")
def reset_scenario(scenario_id: UUID, session: Session = Depends(get_session)) -> dict[str, str]:
    scenario_repo = ScenarioRepository(session)
    scenario = scenario_repo.update_status(scenario_id, "ready")
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    runner = SimulationRunner(session)
    runner.reset(scenario_id)
    return {"status": "ready"}


@router.post("/{scenario_id}/events")
def inject_world_event(
    scenario_id: UUID,
    tick: int,
    event_key: str,
    content: str,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    scenario_repo = ScenarioRepository(session)
    if not scenario_repo.get(scenario_id):
        raise HTTPException(status_code=404, detail="Scenario not found")
    repo = SocialRepository(session)
    row = repo.add_world_event(
        scenario_id=scenario_id,
        tick_number=tick,
        event_key=event_key,
        content=content,
        payload={"valence": "neutral", "urgency": 0.5},
    )
    return {"event_id": str(row.id), "status": "queued"}


def _clone_scenario_with_overrides(
    session: Session,
    source_scenario_id: UUID,
    variant_name: str,
    persona_overrides: dict[str, dict[str, float | str]],
) -> Scenario:
    source = session.get(Scenario, source_scenario_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source scenario not found")

    source_agents = list(session.exec(select(Agent).where(Agent.scenario_id == source_scenario_id)))
    persona_by_agent_name: dict[str, dict] = {}
    for agent in source_agents:
        persona = session.get(PersonaProfile, agent.persona_profile_id)
        if persona:
            persona_by_agent_name[agent.name] = {
                "label": persona.label,
                "communication_style": persona.communication_style,
                "risk_tolerance": persona.risk_tolerance,
                "cooperation_tendency": persona.cooperation_tendency,
                "memory_sensitivity": persona.memory_sensitivity,
                "emotional_bias": persona.emotional_bias,
                "priority_weights": persona.priority_weights,
                "reaction_biases": persona.reaction_biases,
            }

    merged_personas = merge_persona_overrides(persona_by_agent_name, persona_overrides)

    variant = Scenario(
        name=build_variant_name(source.name, variant_name),
        description=f"Variant of {source.name}",
        status="ready",
    )
    session.add(variant)
    session.commit()
    session.refresh(variant)

    old_to_new_agent: dict[UUID, UUID] = {}
    for source_agent in source_agents:
        merged = merged_personas.get(source_agent.name, persona_by_agent_name[source_agent.name])
        persona = PersonaProfile(
            label=str(merged.get("label", "variant")),
            communication_style=str(merged.get("communication_style", "neutral")),
            risk_tolerance=float(merged.get("risk_tolerance", 0.5)),
            cooperation_tendency=float(merged.get("cooperation_tendency", 0.5)),
            memory_sensitivity=float(merged.get("memory_sensitivity", 0.5)),
            emotional_bias=float(merged.get("emotional_bias", 0.0)),
            priority_weights=merged.get("priority_weights", {}),
            reaction_biases=merged.get("reaction_biases", {}),
        )
        session.add(persona)
        session.commit()
        session.refresh(persona)

        cloned_agent = Agent(
            scenario_id=variant.id,
            persona_profile_id=persona.id,
            name=source_agent.name,
            is_active=source_agent.is_active,
        )
        session.add(cloned_agent)
        session.commit()
        session.refresh(cloned_agent)
        old_to_new_agent[source_agent.id] = cloned_agent.id

        first_state = session.exec(
            select(AgentStateSnapshot)
            .where(AgentStateSnapshot.agent_id == source_agent.id)
            .order_by(AgentStateSnapshot.tick_number.asc())
        ).first()
        if first_state:
            session.add(
                AgentStateSnapshot(
                    agent_id=cloned_agent.id,
                    tick_number=0,
                    mood=first_state.mood,
                    active_goals=first_state.active_goals,
                    beliefs=first_state.beliefs,
                    energy=first_state.energy,
                    stress=first_state.stress,
                )
            )
    session.commit()

    source_relationships = list(
        session.exec(select(Relationship).where(Relationship.scenario_id == source_scenario_id))
    )
    for rel in source_relationships:
        if rel.source_agent_id in old_to_new_agent and rel.target_agent_id in old_to_new_agent:
            session.add(
                Relationship(
                    scenario_id=variant.id,
                    source_agent_id=old_to_new_agent[rel.source_agent_id],
                    target_agent_id=old_to_new_agent[rel.target_agent_id],
                    trust=rel.trust,
                    affinity=rel.affinity,
                    stance=rel.stance,
                    influence=rel.influence,
                    last_updated_tick=0,
                )
            )

    source_world_events = list(
        session.exec(
            select(ScenarioEventInjection).where(ScenarioEventInjection.scenario_id == source_scenario_id)
        )
    )
    for world_event in source_world_events:
        session.add(
            ScenarioEventInjection(
                scenario_id=variant.id,
                tick_number=world_event.tick_number,
                event_key=world_event.event_key,
                event_content=world_event.event_content,
                payload=world_event.payload,
                is_consumed=False,
            )
        )
    session.commit()

    return variant


def _scenario_counts(session: Session, scenario_id: UUID) -> dict[str, float]:
    decisions = list(session.exec(select(DecisionLog).where(DecisionLog.scenario_id == scenario_id)))
    messages = list(session.exec(select(Message).where(Message.scenario_id == scenario_id)))
    relationships = list(session.exec(select(Relationship).where(Relationship.scenario_id == scenario_id)))
    avg_trust = sum(item.trust for item in relationships) / len(relationships) if relationships else 0.0
    return {
        "decision_count": len(decisions),
        "message_count": len(messages),
        "avg_trust": avg_trust,
    }


@router.post("/{scenario_id}/compare-rerun", response_model=CompareRerunResponse)
def compare_rerun(
    scenario_id: UUID,
    request: CompareRerunRequest,
    session: Session = Depends(get_session),
) -> CompareRerunResponse:
    scenario_repo = ScenarioRepository(session)
    source = scenario_repo.get(scenario_id)
    if not source:
        raise HTTPException(status_code=404, detail="Scenario not found")

    runner = SimulationRunner(session)
    base = _clone_scenario_with_overrides(
        session=session,
        source_scenario_id=scenario_id,
        variant_name="baseline",
        persona_overrides={},
    )
    variant = _clone_scenario_with_overrides(
        session=session,
        source_scenario_id=scenario_id,
        variant_name=request.variant_name,
        persona_overrides=request.persona_overrides,
    )

    base_run = RunMetadata(
        scenario_id=base.id,
        source_scenario_id=scenario_id,
        run_kind="baseline",
        variant_name="baseline",
        ticks_requested=request.ticks,
        persona_overrides={},
        started_at=datetime.utcnow(),
    )
    variant_run = RunMetadata(
        scenario_id=variant.id,
        source_scenario_id=scenario_id,
        run_kind="variant",
        variant_name=request.variant_name,
        ticks_requested=request.ticks,
        persona_overrides=request.persona_overrides,
        started_at=datetime.utcnow(),
    )
    session.add(base_run)
    session.add(variant_run)
    session.commit()
    session.refresh(base_run)
    session.refresh(variant_run)

    runner.run(base.id, request.ticks)
    runner.run(variant.id, request.ticks)

    base_run.ended_at = datetime.utcnow()
    variant_run.ended_at = datetime.utcnow()
    session.add(base_run)
    session.add(variant_run)

    base_counts = _scenario_counts(session, base.id)
    variant_counts = _scenario_counts(session, variant.id)
    differences = {
        "decision_count_delta": variant_counts["decision_count"] - base_counts["decision_count"],
        "message_count_delta": variant_counts["message_count"] - base_counts["message_count"],
        "relationship_avg_trust_delta": round(variant_counts["avg_trust"] - base_counts["avg_trust"], 6),
    }

    summary = RunComparisonSummary(
        base_run_id=base_run.id,
        variant_run_id=variant_run.id,
        base_scenario_id=base.id,
        variant_scenario_id=variant.id,
        decision_count_delta=differences["decision_count_delta"],
        message_count_delta=differences["message_count_delta"],
        relationship_avg_trust_delta=differences["relationship_avg_trust_delta"],
    )
    session.add(summary)
    session.commit()
    session.refresh(summary)

    repo = SocialRepository(session)
    repo.add_event(
        SimulationEvent(
            scenario_id=variant.id,
            tick_number=request.ticks,
            event_type=SimulationEventType.SYSTEM.value,
            content="comparison_summary",
            payload={
                "summary_id": str(summary.id),
                "base_run_id": str(base_run.id),
                "variant_run_id": str(variant_run.id),
                "differences": differences,
            },
            created_at=datetime.utcnow(),
        )
    )

    return CompareRerunResponse(
        base_scenario_id=base.id,
        variant_scenario_id=variant.id,
        comparison={
            "comparison_id": str(summary.id),
            "base_run_id": str(base_run.id),
            "variant_run_id": str(variant_run.id),
            "differences": differences,
        },
    )
