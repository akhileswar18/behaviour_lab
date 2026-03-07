from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_session
from app.persistence.models import PersonaProfile
from app.persistence.repositories.agent_repository import AgentRepository
from app.persistence.repositories.planning_repository import PlanningRepository
from app.persistence.repositories.world_repository import WorldRepository

router = APIRouter(prefix="/scenarios", tags=["agents"])


@router.get("/{scenario_id}/agents")
def list_agents(scenario_id: UUID, session: Session = Depends(get_session)) -> list[dict]:
    agent_repo = AgentRepository(session)
    planning_repo = PlanningRepository(session)
    world_repo = WorldRepository(session)
    rows = agent_repo.list_by_scenario(scenario_id)
    zones = {zone.id: zone for zone in world_repo.list_zones(scenario_id)}
    result: list[dict] = []
    for row in rows:
        state = agent_repo.latest_state(row.id)
        persona = session.get(PersonaProfile, row.persona_profile_id)
        active_goal = planning_repo.active_goal(scenario_id, row.id)
        active_intention = planning_repo.active_intention(scenario_id, row.id)
        goals: list[str] = state.active_goals if state and state.active_goals else []
        zone_name = zones[state.zone_id].name if state and state.zone_id in zones else None
        result.append(
            {
                "id": str(row.id),
                "scenario_id": str(row.scenario_id),
                "name": row.name,
                "persona_label": persona.label if persona else "persona",
                "communication_style": persona.communication_style if persona else "neutral",
                "cooperation_tendency": persona.cooperation_tendency if persona else 0.0,
                "risk_tolerance": persona.risk_tolerance if persona else 0.0,
                "memory_sensitivity": persona.memory_sensitivity if persona else 0.0,
                "emotional_bias": persona.emotional_bias if persona else 0.0,
                "mood": state.mood if state else "neutral",
                "active_goals": goals,
                "hunger": state.hunger if state else 0.0,
                "safety_need": state.safety_need if state else 0.0,
                "social_need": state.social_need if state else 0.0,
                "zone_id": str(state.zone_id) if state and state.zone_id else None,
                "zone_name": zone_name,
                "inventory": state.inventory if state else {},
                "active_goal": active_goal.goal_type if active_goal else None,
                "active_intention": active_intention.current_action_type if active_intention else None,
            }
        )
    return result
