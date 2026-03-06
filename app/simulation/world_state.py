from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Agent, ScenarioEventInjection, SimulationEvent
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
    return {
        "agents": agents,
        "events": recent_events,
        "world_events": world_events,
    }


def mark_world_events_consumed(session: Session, world_events: list[ScenarioEventInjection]) -> None:
    repo = SocialRepository(session)
    for world_event in world_events:
        repo.mark_world_event_consumed(world_event.id)
