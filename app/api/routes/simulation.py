from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_session
from app.persistence.models import (
    Agent,
    AgentStateSnapshot,
    Goal,
    Intention,
    PersonaProfile,
    Relationship,
    Resource,
    RunComparisonSummary,
    Scenario,
    ScenarioEventInjection,
    SimulationEvent,
    Zone,
)
from app.persistence.repositories.social_repository import SocialRepository
from app.persistence.repositories.scenario_repository import ScenarioRepository
from app.schemas.api import CompareRerunRequest, CompareRerunResponse, RunRequest, RunResponse, TickResultRead
from app.schemas.decision_engine import LlmConfig, PolicyMode
from app.schemas.social import GoalStatus, SimulationEventType
from app.simulation.runner import SimulationRunner
from app.simulation.scenario_loader import (
    build_variant_name,
    merge_agent_state_overrides,
    merge_persona_overrides,
    merge_world_overrides,
)

router = APIRouter(prefix="/scenarios", tags=["simulation"])


@router.post("/{scenario_id}/run", response_model=RunResponse)
def run_scenario(scenario_id: UUID, request: RunRequest, session: Session = Depends(get_session)) -> RunResponse:
    scenario_repo = ScenarioRepository(session)
    scenario = scenario_repo.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario_repo.update_status(scenario_id, "running")
    runner = SimulationRunner(session)
    mode = request.policy_mode or PolicyMode.DETERMINISTIC
    llm_config = LlmConfig.model_validate(request.llm_config or {})
    rows = runner.run(
        scenario_id,
        request.ticks,
        policy_mode=mode,
        llm_config=llm_config,
        source_scenario_id=scenario_id,
        run_kind="direct_run",
        variant_name="direct_run",
    )
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
        policy_mode=runner.last_run_summary.policy_mode,
        fallback_count=runner.last_run_summary.fallback_count,
        llm_decision_count=runner.last_run_summary.llm_decision_count,
        deterministic_decision_count=runner.last_run_summary.deterministic_decision_count,
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
    planning_overrides: dict[str, dict[str, float | str | int]],
    world_overrides: dict[str, dict[str, float | str | int]],
) -> Scenario:
    source = session.get(Scenario, source_scenario_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source scenario not found")

    source_agents = list(session.exec(select(Agent).where(Agent.scenario_id == source_scenario_id)))
    source_zones = list(session.exec(select(Zone).where(Zone.scenario_id == source_scenario_id)))
    source_resources = list(session.exec(select(Resource).where(Resource.scenario_id == source_scenario_id)))
    source_goals = list(session.exec(select(Goal).where(Goal.scenario_id == source_scenario_id)))
    source_intentions = list(session.exec(select(Intention).where(Intention.scenario_id == source_scenario_id)))
    source_relationships = list(session.exec(select(Relationship).where(Relationship.scenario_id == source_scenario_id)))
    source_world_events = list(session.exec(select(ScenarioEventInjection).where(ScenarioEventInjection.scenario_id == source_scenario_id)))

    persona_by_agent_name: dict[str, dict] = {}
    state_by_agent_name: dict[str, dict] = {}
    for agent in source_agents:
        persona = session.get(PersonaProfile, agent.persona_profile_id)
        latest_state = session.exec(
            select(AgentStateSnapshot)
            .where(AgentStateSnapshot.agent_id == agent.id)
            .order_by(AgentStateSnapshot.tick_number.asc())
        ).first()
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
        if latest_state:
            state_by_agent_name[agent.name] = {
                "mood": latest_state.mood,
                "active_goals": latest_state.active_goals,
                "beliefs": latest_state.beliefs,
                "energy": latest_state.energy,
                "stress": latest_state.stress,
                "hunger": latest_state.hunger,
                "safety_need": latest_state.safety_need,
                "social_need": latest_state.social_need,
                "zone_id": latest_state.zone_id,
                "inventory": latest_state.inventory,
            }

    merged_personas = merge_persona_overrides(persona_by_agent_name, persona_overrides)
    merged_states = merge_agent_state_overrides(state_by_agent_name, planning_overrides)

    zone_seed_map = {zone.name: {"zone_type": zone.zone_type, **zone.zone_metadata} for zone in source_zones}
    merged_world = merge_world_overrides(zone_seed_map, world_overrides)

    variant = Scenario(
        name=build_variant_name(source.name, variant_name),
        description=f"Variant of {source.name}",
        status="ready",
    )
    session.add(variant)
    session.commit()
    session.refresh(variant)

    zone_id_map: dict[UUID, UUID] = {}
    zone_by_name: dict[str, Zone] = {}
    for zone in source_zones:
        merged_zone = merged_world.get(zone.name, {})
        cloned_zone = Zone(
            scenario_id=variant.id,
            name=zone.name,
            zone_type=str(merged_zone.get("zone_type", zone.zone_type)),
            zone_metadata={k: v for k, v in merged_zone.items() if k != "zone_type"},
        )
        session.add(cloned_zone)
        session.commit()
        session.refresh(cloned_zone)
        zone_id_map[zone.id] = cloned_zone.id
        zone_by_name[cloned_zone.name] = cloned_zone

    resource_id_map: dict[UUID, UUID] = {}
    for resource in source_resources:
        zone_name = next((z.name for z in source_zones if z.id == resource.zone_id), None)
        zone_override = world_overrides.get(zone_name or "", {})
        quantity_override = zone_override.get(resource.resource_type)
        cloned_resource = Resource(
            scenario_id=variant.id,
            zone_id=zone_id_map[resource.zone_id],
            resource_type=resource.resource_type,
            quantity=int(quantity_override if quantity_override is not None else resource.quantity),
            status=resource.status,
        )
        session.add(cloned_resource)
        session.commit()
        session.refresh(cloned_resource)
        resource_id_map[resource.id] = cloned_resource.id

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

        state = merged_states.get(source_agent.name, {})
        zone_id = state.get("zone_id")
        if isinstance(zone_id, str) and zone_id in zone_by_name:
            zone_id = zone_by_name[zone_id].id
        elif zone_id in zone_id_map:
            zone_id = zone_id_map[zone_id]
        session.add(
            AgentStateSnapshot(
                agent_id=cloned_agent.id,
                tick_number=0,
                mood=str(state.get("mood", "neutral")),
                active_goals=list(state.get("active_goals", [])),
                beliefs=state.get("beliefs", {}),
                energy=float(state.get("energy", 100.0)),
                stress=float(state.get("stress", 0.0)),
                hunger=float(state.get("hunger", 0.0)),
                safety_need=float(state.get("safety_need", 0.0)),
                social_need=float(state.get("social_need", 0.0)),
                zone_id=zone_id,
                inventory=state.get("inventory", {}),
            )
        )
    session.commit()

    goal_id_map: dict[UUID, UUID] = {}
    for goal in source_goals:
        cloned_goal = Goal(
            scenario_id=variant.id,
            agent_id=old_to_new_agent[goal.agent_id],
            goal_type=goal.goal_type,
            priority=goal.priority,
            status=goal.status,
            target=goal.target,
            source=goal.source,
        )
        session.add(cloned_goal)
        session.commit()
        session.refresh(cloned_goal)
        goal_id_map[goal.id] = cloned_goal.id

    for intention in source_intentions:
        session.add(
            Intention(
                scenario_id=variant.id,
                agent_id=old_to_new_agent[intention.agent_id],
                goal_id=goal_id_map.get(intention.goal_id) if intention.goal_id else None,
                current_action_type=intention.current_action_type,
                status=intention.status,
                rationale=intention.rationale,
                target_zone_id=zone_id_map.get(intention.target_zone_id) if intention.target_zone_id else None,
                target_resource_id=resource_id_map.get(intention.target_resource_id) if intention.target_resource_id else None,
                is_interruptible=intention.is_interruptible,
            )
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

    for world_event in source_world_events:
        payload = dict(world_event.payload or {})
        zone_name = payload.get("zone")
        if zone_name and zone_name in world_overrides:
            payload.update(world_overrides[zone_name])
        session.add(
            ScenarioEventInjection(
                scenario_id=variant.id,
                tick_number=world_event.tick_number,
                event_key=world_event.event_key,
                event_content=world_event.event_content,
                payload=payload,
                is_consumed=False,
            )
        )
    session.commit()

    return variant


def _scenario_counts(session: Session, scenario_id: UUID) -> dict[str, float]:
    decisions = list(session.exec(select(SimulationEvent).where(SimulationEvent.scenario_id == scenario_id)))
    messages = [event for event in decisions if event.event_type == SimulationEventType.MESSAGE.value]
    relationships = [event for event in decisions if event.event_type == SimulationEventType.RELATIONSHIP_UPDATE.value]
    move_events = [event for event in decisions if event.event_type == SimulationEventType.MOVE.value]
    resource_events = [event for event in decisions if event.event_type in {SimulationEventType.ACQUIRE.value, SimulationEventType.CONSUME.value}]
    goals = list(session.exec(select(Goal).where(Goal.scenario_id == scenario_id)))
    relationship_rows = list(session.exec(select(Relationship).where(Relationship.scenario_id == scenario_id)))
    avg_trust = sum(item.trust for item in relationship_rows) / len(relationship_rows) if relationship_rows else 0.0
    completed_goals = len([goal for goal in goals if goal.status == GoalStatus.COMPLETED.value])
    return {
        "decision_count": len([event for event in decisions if event.event_type == SimulationEventType.DECISION.value]),
        "message_count": len(messages),
        "avg_trust": avg_trust,
        "completed_goal_count": completed_goals,
        "move_event_count": len(move_events),
        "resource_event_count": len(resource_events),
        "relationship_record_count": len(relationships),
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
        planning_overrides={},
        world_overrides={},
    )
    variant = _clone_scenario_with_overrides(
        session=session,
        source_scenario_id=scenario_id,
        variant_name=request.variant_name,
        persona_overrides=request.persona_overrides,
        planning_overrides=request.planning_overrides,
        world_overrides=request.world_overrides,
    )

    base_llm_config = LlmConfig.model_validate(request.base_llm_config or {})
    variant_llm_config = LlmConfig.model_validate(request.variant_llm_config or {})
    runner.run(
        base.id,
        request.ticks,
        policy_mode=request.base_policy_mode,
        llm_config=base_llm_config,
        source_scenario_id=scenario_id,
        run_kind="baseline",
        variant_name="baseline",
        persona_overrides={},
        planning_overrides={},
        world_overrides={},
    )
    base_run_id = runner.last_run_summary.run_metadata_id
    base_fallback_count = runner.last_run_summary.fallback_count
    base_llm_count = runner.last_run_summary.llm_decision_count
    runner.run(
        variant.id,
        request.ticks,
        policy_mode=request.variant_policy_mode,
        llm_config=variant_llm_config,
        source_scenario_id=scenario_id,
        run_kind="variant",
        variant_name=request.variant_name,
        persona_overrides=request.persona_overrides,
        planning_overrides=request.planning_overrides,
        world_overrides=request.world_overrides,
    )
    variant_run_id = runner.last_run_summary.run_metadata_id
    variant_fallback_count = runner.last_run_summary.fallback_count
    variant_llm_count = runner.last_run_summary.llm_decision_count
    if base_run_id is None or variant_run_id is None:
        raise HTTPException(status_code=500, detail="Run metadata missing for comparison rerun")

    base_counts = _scenario_counts(session, base.id)
    variant_counts = _scenario_counts(session, variant.id)
    differences = {
        "decision_count_delta": variant_counts["decision_count"] - base_counts["decision_count"],
        "message_count_delta": variant_counts["message_count"] - base_counts["message_count"],
        "relationship_avg_trust_delta": round(variant_counts["avg_trust"] - base_counts["avg_trust"], 6),
        "completed_goal_delta": variant_counts["completed_goal_count"] - base_counts["completed_goal_count"],
        "move_event_delta": variant_counts["move_event_count"] - base_counts["move_event_count"],
        "resource_event_delta": variant_counts["resource_event_count"] - base_counts["resource_event_count"],
        "fallback_count_delta": variant_fallback_count - base_fallback_count,
        "llm_decision_delta": variant_llm_count - base_llm_count,
    }

    summary = RunComparisonSummary(
        base_run_id=base_run_id,
        variant_run_id=variant_run_id,
        base_scenario_id=base.id,
        variant_scenario_id=variant.id,
        decision_count_delta=differences["decision_count_delta"],
        message_count_delta=differences["message_count_delta"],
        relationship_avg_trust_delta=differences["relationship_avg_trust_delta"],
        completed_goal_delta=differences["completed_goal_delta"],
        move_event_delta=differences["move_event_delta"],
        resource_event_delta=differences["resource_event_delta"],
        fallback_count_delta=differences["fallback_count_delta"],
        llm_decision_delta=differences["llm_decision_delta"],
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
                "base_run_id": str(base_run_id),
                "variant_run_id": str(variant_run_id),
                "base_policy_mode": request.base_policy_mode.value,
                "variant_policy_mode": request.variant_policy_mode.value,
                "differences": differences,
            },
            created_at=datetime.utcnow(),
        )
    )

    return CompareRerunResponse(
        base_scenario_id=base.id,
        variant_scenario_id=variant.id,
        base_policy_mode=request.base_policy_mode.value,
        variant_policy_mode=request.variant_policy_mode.value,
        comparison={
            "comparison_id": str(summary.id),
            "base_run_id": str(base_run_id),
            "variant_run_id": str(variant_run_id),
            "base_policy_mode": request.base_policy_mode.value,
            "variant_policy_mode": request.variant_policy_mode.value,
            "differences": differences,
        },
    )
