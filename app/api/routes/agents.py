from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_session
from app.persistence.models import PersonaProfile
from app.persistence.repositories.agent_repository import AgentRepository

router = APIRouter(prefix="/scenarios", tags=["agents"])


@router.get("/{scenario_id}/agents")
def list_agents(scenario_id: UUID, session: Session = Depends(get_session)) -> list[dict]:
    repo = AgentRepository(session)
    rows = repo.list_by_scenario(scenario_id)
    result: list[dict] = []
    for row in rows:
        state = repo.latest_state(row.id)
        persona = session.get(PersonaProfile, row.persona_profile_id)
        goals: list[str] = state.active_goals if state and state.active_goals else []
        result.append(
            {
                "id": str(row.id),
                "scenario_id": str(row.scenario_id),
                "name": row.name,
                "persona_label": persona.label if persona else "persona",
                "mood": state.mood if state else "neutral",
                "active_goals": goals,
            }
        )
    return result
