from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import Session

from app.agents.decision_engine import DecisionEngine
from app.agents.models import AgentConfig
from app.agents.planning_policy import resolve_goal_status, resolve_intention_status, select_plan
from app.agents.relationship_policy import compute_relationship_delta, derive_stance
from app.communication.handlers import emit_agent_message
from app.memory.retriever import retrieve_relevant
from app.memory.summarizer import score_salience
from app.memory.writer import create_memory
from app.persistence.models import (
    AgentStateSnapshot,
    DecisionLog,
    Goal,
    Intention,
    MemoryRetrievalTrace,
    PersonaProfile,
    Resource,
    SimulationEvent,
    TickResult,
)
from app.persistence.repositories.agent_repository import AgentRepository
from app.persistence.repositories.memory_repository import MemoryRepository
from app.persistence.repositories.planning_repository import PlanningRepository
from app.persistence.repositories.social_repository import SocialRepository
from app.persistence.repositories.world_repository import WorldRepository
from app.schemas.decision_engine import (
    DecisionConstraints,
    DecisionContext,
    LlmConfig,
    PolicyMode,
)
from app.schemas.settings import get_settings
from app.schemas.social import GoalStatus, IntentionStatus, SimulationEventType, SocialAction
from app.simulation.world_state import build_tick_context, mark_world_events_consumed


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


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
        "hunger": latest_state.hunger if latest_state else 0.0,
        "safety_need": latest_state.safety_need if latest_state else 0.0,
        "social_need": latest_state.social_need if latest_state else 0.0,
        "inventory": latest_state.inventory if latest_state else {},
    }
    return AgentConfig(name=agent_name, persona=persona_payload, initial_state=state_payload)


def _pick_receiver(agent_id: UUID, peer_ids: list[UUID]) -> UUID | None:
    for peer_id in peer_ids:
        if peer_id != agent_id:
            return peer_id
    return None


def _resource_status(resource: Resource) -> str:
    if resource.quantity <= 0:
        return "depleted"
    if resource.quantity <= 1:
        return "low"
    return "available"


def _progress_needs(latest_state: AgentStateSnapshot | None, urgent_here: bool) -> dict[str, object]:
    settings = get_settings()
    latest_state = latest_state or AgentStateSnapshot(agent_id=UUID(int=0))
    inventory = dict(latest_state.inventory or {})
    hunger = _clamp(float(getattr(latest_state, "hunger", 0.0)) + settings.hunger_tick_delta)
    social_need = _clamp(float(getattr(latest_state, "social_need", 0.0)) + settings.social_need_tick_delta)
    safety_base = float(getattr(latest_state, "safety_need", 0.0))
    safety_need = _clamp(safety_base + (0.25 if urgent_here else -settings.safety_decay_per_tick))
    return {
        "hunger": hunger,
        "social_need": social_need,
        "safety_need": safety_need,
        "inventory": inventory,
    }


def _ensure_goal_and_intention(
    session: Session,
    planning_repo: PlanningRepository,
    scenario_id: UUID,
    agent_id: UUID,
    plan: dict,
    active_goal: Goal | None,
    active_intention: Intention | None,
    tick_number: int,
) -> tuple[Goal, Intention, list[SimulationEvent]]:
    events: list[SimulationEvent] = []
    now = datetime.utcnow()
    goal_changed = active_goal is None or active_goal.goal_type != plan["goal_type"]
    if active_goal is not None and goal_changed:
        active_goal.status = GoalStatus.INTERRUPTED.value if plan.get("interrupt") else GoalStatus.DEFERRED.value
        active_goal.updated_at = now
        planning_repo.save_goal(active_goal)
    if goal_changed:
        goal = planning_repo.add_goal(
            Goal(
                scenario_id=scenario_id,
                agent_id=agent_id,
                goal_type=plan["goal_type"],
                priority=float(plan.get("goal_priority", 0.5)),
                status=GoalStatus.ACTIVE.value,
                target=plan.get("goal_target", {}),
                source=str(plan.get("goal_source", "runtime")),
                created_at=now,
                updated_at=now,
            )
        )
        events.append(
            SimulationEvent(
                scenario_id=scenario_id,
                tick_number=tick_number,
                event_type=SimulationEventType.PLAN_CHANGE.value,
                actor_agent_id=agent_id,
                content=f"goal_changed:{goal.goal_type}",
                payload={"goal_id": str(goal.id), "goal_type": goal.goal_type, "reason": plan.get("rationale", "")},
                created_at=now,
            )
        )
    else:
        goal = active_goal
        goal.priority = float(plan.get("goal_priority", goal.priority))
        goal.target = plan.get("goal_target", goal.target)
        goal.updated_at = now
        planning_repo.save_goal(goal)

    intention_changed = (
        active_intention is None
        or active_intention.current_action_type != plan["action"]
        or str(active_intention.target_zone_id or "") != str(plan.get("target_zone_id") or "")
        or str(active_intention.target_resource_id or "") != str(plan.get("target_resource_id") or "")
        or plan.get("interrupt", False)
    )
    if active_intention is not None and intention_changed:
        active_intention.status = IntentionStatus.INTERRUPTED.value if plan.get("interrupt") else IntentionStatus.DEFERRED.value
        active_intention.updated_at = now
        planning_repo.save_intention(active_intention)
        if plan.get("interrupt"):
            events.append(
                SimulationEvent(
                    scenario_id=scenario_id,
                    tick_number=tick_number,
                    event_type=SimulationEventType.INTERRUPTION.value,
                    actor_agent_id=agent_id,
                    content=f"interruption:{plan['goal_type']}",
                    payload={
                        "previous_intention_id": str(active_intention.id),
                        "goal_type": plan["goal_type"],
                        "reason": plan.get("rationale", ""),
                    },
                    created_at=now,
                )
            )
    if intention_changed:
        intention = planning_repo.add_intention(
            Intention(
                scenario_id=scenario_id,
                agent_id=agent_id,
                goal_id=goal.id,
                current_action_type=plan["action"],
                status=IntentionStatus.ACTIVE.value,
                rationale=str(plan.get("rationale", "")),
                target_zone_id=plan.get("target_zone_id"),
                target_resource_id=plan.get("target_resource_id"),
                is_interruptible=True,
                started_at=now,
                updated_at=now,
            )
        )
    else:
        intention = active_intention
        intention.rationale = str(plan.get("rationale", intention.rationale))
        intention.updated_at = now
        planning_repo.save_intention(intention)

    return goal, intention, events


def run_tick(
    session: Session,
    scenario_id: UUID,
    tick_number: int,
    policy_mode: PolicyMode = PolicyMode.DETERMINISTIC,
    llm_config: LlmConfig | None = None,
    decision_engine: DecisionEngine | None = None,
) -> TickResult:
    settings = get_settings()
    agent_repo = AgentRepository(session)
    memory_repo = MemoryRepository(session)
    social_repo = SocialRepository(session)
    planning_repo = PlanningRepository(session)
    world_repo = WorldRepository(session)
    effective_engine = decision_engine or DecisionEngine()
    effective_llm_config = llm_config or LlmConfig(
        provider=settings.llm_provider,
        model=settings.llm_model,
        endpoint=settings.llm_endpoint,
        timeout_seconds=settings.llm_timeout_seconds,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.llm_api_key,
        debug_store_prompt=settings.llm_debug_store_prompt,
    )

    context = build_tick_context(session, scenario_id, tick_number)
    agents = context["agents"]
    recent_events = context["events"]
    world_events = context["world_events"]
    zones = context["zones"]
    resources = context["resources"]
    occupancy = context["occupancy"]
    latest_state_by_agent = context["latest_state_by_agent"]
    zones_by_id = {zone.id: zone for zone in zones}
    zones_by_name = {zone.name: zone for zone in zones}

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
        latest_state = latest_state_by_agent.get(agent.id) or agent_repo.latest_state(agent.id)
        agent_cfg = _build_agent_config(agent.name, persona, latest_state)
        current_zone = zones_by_id.get(latest_state.zone_id) if latest_state and latest_state.zone_id else None
        local_resources = [resource for resource in resources if current_zone and resource.zone_id == current_zone.id]
        urgent_here = any(
            float((world_event.payload or {}).get("urgency", 0.0)) >= settings.interruption_urgency_threshold
            and ((world_event.payload or {}).get("zone") in {None, current_zone.name if current_zone else None})
            for world_event in world_events
        )
        progressed = _progress_needs(latest_state, urgent_here)
        observed_events = [
            {"event_type": event.event_type, "content": event.content, "payload": event.payload}
            for event in recent_events
        ] + world_event_observed
        recalled = retrieve_relevant(session, agent.id, limit=3)
        relationships = social_repo.list_relationships(scenario_id, agent.id)
        outbound_relationship = next((r for r in relationships if r.source_agent_id == agent.id), None)
        relationship_context = {
            "trust": outbound_relationship.trust if outbound_relationship else 0.0,
            "affinity": outbound_relationship.affinity if outbound_relationship else 0.0,
        }
        active_goal = planning_repo.active_goal(scenario_id, agent.id)
        active_intention = planning_repo.active_intention(scenario_id, agent.id)
        urgent_events = [item for item in world_event_observed if float(item.get("payload", {}).get("urgency", 0.0)) >= settings.interruption_urgency_threshold]
        plan = select_plan(
            latest_state=AgentStateSnapshot(
                agent_id=agent.id,
                hunger=float(progressed["hunger"]),
                safety_need=float(progressed["safety_need"]),
                social_need=float(progressed["social_need"]),
                zone_id=current_zone.id if current_zone else None,
                inventory=progressed["inventory"],
            ),
            active_goal=active_goal,
            active_intention=active_intention,
            zone=current_zone,
            local_resources=local_resources,
            all_resources=resources,
            urgent_events=urgent_events,
        )
        if plan.get("target_zone_id") is None:
            target_zone_name = str(plan.get("goal_target", {}).get("zone", "")).strip()
            if target_zone_name in zones_by_name:
                plan["target_zone_id"] = zones_by_name[target_zone_name].id
        goal, intention, planning_events = _ensure_goal_and_intention(
            session,
            planning_repo,
            scenario_id,
            agent.id,
            plan,
            active_goal,
            active_intention,
            tick_number,
        )
        for event in planning_events:
            social_repo.add_event(event)
            events_created += 1

        prior_hunger = latest_state.hunger if latest_state else 0.0
        prior_safety = latest_state.safety_need if latest_state else 0.0
        prior_social = latest_state.social_need if latest_state else 0.0
        if prior_hunger < settings.severe_need_threshold <= float(progressed["hunger"]):
            social_repo.add_event(
                SimulationEvent(
                    scenario_id=scenario_id,
                    tick_number=tick_number,
                    event_type=SimulationEventType.NEED_THRESHOLD.value,
                    actor_agent_id=agent.id,
                    content="hunger_threshold_crossed",
                    payload={"need": "hunger", "value": progressed["hunger"]},
                    created_at=datetime.utcnow(),
                )
            )
            events_created += 1
        if prior_safety < settings.severe_need_threshold <= float(progressed["safety_need"]):
            social_repo.add_event(
                SimulationEvent(
                    scenario_id=scenario_id,
                    tick_number=tick_number,
                    event_type=SimulationEventType.NEED_THRESHOLD.value,
                    actor_agent_id=agent.id,
                    content="safety_threshold_crossed",
                    payload={"need": "safety_need", "value": progressed["safety_need"]},
                    created_at=datetime.utcnow(),
                )
            )
            events_created += 1
        if prior_social < settings.severe_need_threshold <= float(progressed["social_need"]):
            social_repo.add_event(
                SimulationEvent(
                    scenario_id=scenario_id,
                    tick_number=tick_number,
                    event_type=SimulationEventType.NEED_THRESHOLD.value,
                    actor_agent_id=agent.id,
                    content="social_threshold_crossed",
                    payload={"need": "social_need", "value": progressed["social_need"]},
                    created_at=datetime.utcnow(),
                )
            )
            events_created += 1

        decision_context = DecisionContext(
            scenario_id=scenario_id,
            agent_id=agent.id,
            agent_name=agent.name,
            tick_number=tick_number,
            persona={
                "label": agent_cfg.persona.label,
                "communication_style": agent_cfg.persona.communication_style,
                "risk_tolerance": agent_cfg.persona.risk_tolerance,
                "cooperation_tendency": agent_cfg.persona.cooperation_tendency,
                "memory_sensitivity": agent_cfg.persona.memory_sensitivity,
                "emotional_bias": agent_cfg.persona.emotional_bias,
            },
            needs={
                "hunger": float(progressed["hunger"]),
                "safety_need": float(progressed["safety_need"]),
                "social_need": float(progressed["social_need"]),
            },
            mood=latest_state.mood if latest_state else "neutral",
            zone={
                "id": str(current_zone.id) if current_zone else None,
                "name": current_zone.name if current_zone else None,
            },
            active_goal=(
                {"goal_type": goal.goal_type, "priority": goal.priority, "target": goal.target}
                if goal
                else None
            ),
            active_intention=(
                {
                    "action": intention.current_action_type,
                    "status": intention.status,
                    "target_zone_id": str(intention.target_zone_id)
                    if intention.target_zone_id
                    else None,
                    "target_resource_id": str(intention.target_resource_id)
                    if intention.target_resource_id
                    else None,
                }
                if intention
                else None
            ),
            planning_context=plan,
            observed_events=observed_events,
            relationships=[
                {
                    "source_agent_id": str(rel.source_agent_id),
                    "target_agent_id": str(rel.target_agent_id),
                    "trust": rel.trust,
                    "affinity": rel.affinity,
                    "stance": rel.stance,
                }
                for rel in relationships
            ],
            recalled_memories=[
                {
                    "id": str(memory.id),
                    "tick_number": tick_number,
                    "memory_type": memory.memory_type,
                    "content": memory.content,
                    "relevance_score": 0.8,
                    "salience": memory.salience,
                }
                for memory in recalled
            ],
            local_resources=[
                {
                    "id": str(resource.id),
                    "resource_type": resource.resource_type,
                    "quantity": resource.quantity,
                    "status": resource.status,
                    "zone_id": str(resource.zone_id),
                }
                for resource in local_resources
            ],
        )
        constraints = DecisionConstraints(
            allowed_zone_ids=[str(zone.id) for zone in zones],
            allowed_resource_ids=[str(resource.id) for resource in resources],
            allowed_target_agent_ids=[str(candidate.id) for candidate in agents if candidate.id != agent.id],
        )
        decision_result = effective_engine.resolve(
            context=decision_context,
            mode=policy_mode,
            llm_config=effective_llm_config,
            constraints=constraints,
        )
        decision = decision_result.decision

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
            world_event_factors={
                "world_event_count": len(world_event_observed),
                "zone": current_zone.name if current_zone else None,
                "local_resource_count": len(local_resources),
                "goal_type": goal.goal_type,
            },
            decision_source=decision_result.decision_source.value,
            parser_status=decision_result.parser_status.value,
            fallback_reason=(
                decision_result.fallback_reason.value if decision_result.fallback_reason else None
            ),
            prompt_summary=decision_result.prompt_summary,
            llm_metadata={
                "provider": decision_result.llm_provider,
                "model": decision_result.llm_model,
                "latency_ms": decision_result.llm_latency_ms,
                "error": decision_result.llm_error,
            },
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

        if decision_result.parser_status != decision_result.parser_status.NOT_ATTEMPTED:
            social_repo.add_event(
                SimulationEvent(
                    scenario_id=scenario_id,
                    tick_number=tick_number,
                    event_type=SimulationEventType.SYSTEM.value,
                    actor_agent_id=agent.id,
                    content=f"llm_parse_status:{decision_result.parser_status.value}",
                    payload={
                        "decision_id": str(decision_log.id),
                        "parser_status": decision_result.parser_status.value,
                        "policy_mode": policy_mode.value,
                    },
                    created_at=datetime.utcnow(),
                )
            )
            events_created += 1

        if decision_result.fallback_reason is not None:
            social_repo.add_event(
                SimulationEvent(
                    scenario_id=scenario_id,
                    tick_number=tick_number,
                    event_type=SimulationEventType.INTERRUPTION.value,
                    actor_agent_id=agent.id,
                    content="llm_fallback_triggered",
                    payload={
                        "decision_id": str(decision_log.id),
                        "fallback_reason": decision_result.fallback_reason.value,
                        "parser_status": decision_result.parser_status.value,
                        "policy_mode": policy_mode.value,
                    },
                    created_at=datetime.utcnow(),
                )
            )
            events_created += 1

        action_succeeded = True
        action_event: SimulationEvent | None = None
        current_inventory = dict(progressed["inventory"])
        next_zone_id = current_zone.id if current_zone else None
        next_hunger = float(progressed["hunger"])
        next_safety = float(progressed["safety_need"])
        next_social = float(progressed["social_need"])

        if decision.action == SocialAction.MOVE.value:
            target_zone_id = UUID(decision.target_zone_id) if decision.target_zone_id else None
            target_zone = zones_by_id.get(target_zone_id) if target_zone_id else None
            if target_zone is None and plan.get("goal_target", {}).get("zone") in zones_by_name:
                target_zone = zones_by_name[plan["goal_target"]["zone"]]
            if target_zone is not None:
                next_zone_id = target_zone.id
                action_event = social_repo.add_event(
                    SimulationEvent(
                        scenario_id=scenario_id,
                        tick_number=tick_number,
                        event_type=SimulationEventType.MOVE.value,
                        actor_agent_id=agent.id,
                        content=f"{agent.name} moved to {target_zone.name}",
                        payload={
                            "decision_id": str(decision_log.id),
                            "goal_id": str(goal.id),
                            "intention_id": str(intention.id),
                            "zone_id": str(target_zone.id),
                        },
                        created_at=datetime.utcnow(),
                    )
                )
                next_social = _clamp(next_social - 0.05)
            else:
                action_succeeded = False
        elif decision.action == SocialAction.ACQUIRE_RESOURCE.value:
            target_resource = None
            if decision.target_resource_id:
                target_resource = world_repo.get_resource(UUID(decision.target_resource_id))
            if target_resource is None:
                target_resource = next((resource for resource in local_resources if resource.resource_type == "food" and resource.quantity > 0), None)
            if target_resource is not None and target_resource.quantity > 0:
                target_resource.quantity -= settings.resource_consumption_amount
                target_resource.status = _resource_status(target_resource)
                target_resource.updated_at = datetime.utcnow()
                world_repo.save_resource(target_resource)
                current_inventory[target_resource.resource_type] = current_inventory.get(target_resource.resource_type, 0) + settings.resource_consumption_amount
                action_event = social_repo.add_event(
                    SimulationEvent(
                        scenario_id=scenario_id,
                        tick_number=tick_number,
                        event_type=SimulationEventType.ACQUIRE.value,
                        actor_agent_id=agent.id,
                        content=f"{agent.name} acquired {target_resource.resource_type}",
                        payload={
                            "decision_id": str(decision_log.id),
                            "goal_id": str(goal.id),
                            "intention_id": str(intention.id),
                            "resource_id": str(target_resource.id),
                            "zone_id": str(target_resource.zone_id),
                        },
                        created_at=datetime.utcnow(),
                    )
                )
            else:
                action_succeeded = False
                action_event = social_repo.add_event(
                    SimulationEvent(
                        scenario_id=scenario_id,
                        tick_number=tick_number,
                        event_type=SimulationEventType.RESOURCE_SHORTAGE.value,
                        actor_agent_id=agent.id,
                        content=f"{agent.name} could not acquire food",
                        payload={"decision_id": str(decision_log.id), "goal_id": str(goal.id)},
                        created_at=datetime.utcnow(),
                    )
                )
        elif decision.action == SocialAction.CONSUME_RESOURCE.value:
            if current_inventory.get("food", 0) > 0:
                current_inventory["food"] -= settings.resource_consumption_amount
                next_hunger = _clamp(next_hunger - 0.6)
                action_event = social_repo.add_event(
                    SimulationEvent(
                        scenario_id=scenario_id,
                        tick_number=tick_number,
                        event_type=SimulationEventType.CONSUME.value,
                        actor_agent_id=agent.id,
                        content=f"{agent.name} consumed food",
                        payload={
                            "decision_id": str(decision_log.id),
                            "goal_id": str(goal.id),
                            "intention_id": str(intention.id),
                            "resource_type": "food",
                        },
                        created_at=datetime.utcnow(),
                    )
                )
            else:
                action_succeeded = False
                action_event = social_repo.add_event(
                    SimulationEvent(
                        scenario_id=scenario_id,
                        tick_number=tick_number,
                        event_type=SimulationEventType.RESOURCE_SHORTAGE.value,
                        actor_agent_id=agent.id,
                        content=f"{agent.name} has no food to consume",
                        payload={"decision_id": str(decision_log.id), "goal_id": str(goal.id)},
                        created_at=datetime.utcnow(),
                    )
                )
        else:
            peers_in_zone = occupancy.get(current_zone.id, []) if current_zone else []
            all_peer_ids = [candidate.id for candidate in agents if candidate.id != agent.id]
            peer_ids = [peer_id for peer_id in peers_in_zone if peer_id != agent.id] or all_peer_ids
            receiver_id = _pick_receiver(agent.id, peer_ids)
            if receiver_id is not None:
                message_content = f"{agent.name} {decision.action}s: {decision.rationale}"
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
                trust_delta, affinity_delta = compute_relationship_delta(decision.intent, decision.emotional_tone)
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
                social_repo.add_event(
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
                            "goal_id": str(goal.id),
                        },
                        created_at=datetime.utcnow(),
                    )
                )
                events_created += 1
                next_social = _clamp(next_social - 0.2)
                action_event = message_event
            else:
                action_succeeded = decision.action in {SocialAction.OBSERVE.value, SocialAction.WAIT.value}

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
                    "decision_source": decision_result.decision_source.value,
                    "parser_status": decision_result.parser_status.value,
                    "fallback_reason": (
                        decision_result.fallback_reason.value if decision_result.fallback_reason else None
                    ),
                    "goal_id": str(goal.id),
                    "intention_id": str(intention.id),
                },
                created_at=datetime.utcnow(),
            )
        )
        events_created += 1
        if action_event is not None:
            events_created += 1

        goal.status = resolve_goal_status(decision.action, action_succeeded)
        goal.updated_at = datetime.utcnow()
        planning_repo.save_goal(goal)
        intention.status = resolve_intention_status(decision.action, action_succeeded, bool(plan.get("interrupt")))
        intention.updated_at = datetime.utcnow()
        planning_repo.save_intention(intention)

        memory_repo.add_memory(
            create_memory(
                agent_id=agent.id,
                source_event_id=(action_event.id if action_event is not None else decision_event.id),
                memory_type="decision",
                content=decision.rationale,
                salience=score_salience(0.55, SimulationEventType.DECISION.value),
                valence=agent_cfg.persona.emotional_bias,
            )
        )

        next_mood = {
            SocialAction.MOVE.value: "focused",
            SocialAction.ACQUIRE_RESOURCE.value: "urgent",
            SocialAction.CONSUME_RESOURCE.value: "relieved",
            SocialAction.WARN.value: "alert",
            SocialAction.COOPERATE.value: "engaged",
            SocialAction.AVOID.value: "guarded",
            SocialAction.PROPOSE.value: "focused",
            SocialAction.OBSERVE.value: "curious",
            SocialAction.WAIT.value: "neutral",
        }.get(decision.action, "neutral")
        active_goal_names = [item.goal_type for item in planning_repo.list_goals(scenario_id, agent.id) if item.status == GoalStatus.ACTIVE.value]
        session.add(
            AgentStateSnapshot(
                agent_id=agent.id,
                tick_number=tick_number,
                mood=next_mood,
                active_goals=active_goal_names,
                beliefs=latest_state.beliefs if latest_state else {},
                energy=max((latest_state.energy if latest_state else 100.0) - 1.0, 0.0),
                stress=min((latest_state.stress if latest_state else 0.0) + (0.6 if urgent_here else 0.2), 100.0),
                hunger=next_hunger,
                safety_need=next_safety,
                social_need=next_social,
                zone_id=next_zone_id,
                inventory=current_inventory,
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
