from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.schemas.social import RelationshipRead
from app.api.deps import get_session
from app.persistence.repositories.social_repository import SocialRepository

router = APIRouter(prefix="/scenarios", tags=["relationships"])


@router.get("/{scenario_id}/relationships", response_model=list[RelationshipRead])
def get_relationships(
    scenario_id: UUID,
    agent_id: UUID | None = None,
    session: Session = Depends(get_session),
) -> list[RelationshipRead]:
    repo = SocialRepository(session)
    rows = repo.list_relationships(scenario_id, agent_id=agent_id)
    return [
        RelationshipRead(
            source_agent_id=r.source_agent_id,
            target_agent_id=r.target_agent_id,
            trust=r.trust,
            affinity=r.affinity,
            stance=r.stance,
            influence=r.influence,
            last_updated_tick=r.last_updated_tick,
            last_interaction_at=r.last_interaction_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]
