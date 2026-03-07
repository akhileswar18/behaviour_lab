from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Agent, AgentStateSnapshot, Resource, ScenarioEventInjection, SimulationEvent, Zone
from app.persistence.repositories.social_repository import SocialRepository
from app.schemas.settings import get_settings


def build_tick_context(session: Session, scenario_id: UUID, tick_number: int) -> dict:
    settings = get_settings()
    recent_window = max(settings.recent_event_window, 1)

    agents = list(session.exec(select(Agent).where(Agent.scenario_id == scenario_id)))
    recent_events = list(
        session.exec(
            select(SimulationEvent)
            .where(SimulationEvent.scenario_id == scenario_id)
            .where(SimulationEvent.tick_number >= max(tick_number - recent_window, 0))
            .order_by(SimulationEvent.tick_number, SimulationEvent.created_at)
        )
    )
    world_events = list(
        session.exec(
            select(ScenarioEventInjection)
            .where(ScenarioEventInjection.scenario_id == scenario_id)
            .where(ScenarioEventInjection.tick_number == tick_number)
            .where(ScenarioEventInjection.is_consumed.is_(False))
            .order_by(ScenarioEventInjection.created_at)
        )
    )
    zones = list(session.exec(select(Zone).where(Zone.scenario_id == scenario_id).order_by(Zone.name)))
    resources = list(session.exec(select(Resource).where(Resource.scenario_id == scenario_id).order_by(Resource.resource_type)))

    latest_state_by_agent: dict[UUID, AgentStateSnapshot | None] = {}
    occupancy: dict[UUID, list[UUID]] = defaultdict(list)
    for agent in agents:
        state = session.exec(
            select(AgentStateSnapshot)
            .where(AgentStateSnapshot.agent_id == agent.id)
            .order_by(AgentStateSnapshot.tick_number.desc())
        ).first()
        latest_state_by_agent[agent.id] = state
        if state and state.zone_id is not None:
            occupancy[state.zone_id].append(agent.id)

    return {
        "agents": agents,
        "events": recent_events,
        "world_events": world_events,
        "zones": zones,
        "resources": resources,
        "occupancy": dict(occupancy),
        "latest_state_by_agent": latest_state_by_agent,
    }


def mark_world_events_consumed(session: Session, world_events: list[ScenarioEventInjection]) -> None:
    repo = SocialRepository(session)
    for world_event in world_events:
        repo.mark_world_event_consumed(world_event.id)
