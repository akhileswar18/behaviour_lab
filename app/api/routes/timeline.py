from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_session
from app.api.schemas.social import TimelineEventRead
from app.persistence.repositories.social_repository import SocialRepository

router = APIRouter(prefix="/scenarios", tags=["timeline"])


@router.get("/{scenario_id}/timeline", response_model=list[TimelineEventRead])
def get_timeline(
    scenario_id: UUID,
    tick_from: int | None = None,
    tick_to: int | None = None,
    agent_id: UUID | None = None,
    event_type: str | None = None,
    decision_source: str | None = None,
    zone_id: UUID | None = None,
    limit: int | None = None,
    session: Session = Depends(get_session),
) -> list[TimelineEventRead]:
    repo = SocialRepository(session)
    rows = repo.list_timeline(
        scenario_id,
        tick_from=tick_from,
        tick_to=tick_to,
        agent_id=agent_id,
        event_type=event_type,
        zone_id=zone_id,
    )
    if decision_source is not None:
        rows = [
            row
            for row in rows
            if str((row.payload or {}).get("decision_source", "")) == decision_source
        ]
    return [
        TimelineEventRead(
            id=r.id,
            tick_number=r.tick_number,
            event_type=r.event_type,
            actor_agent_id=r.actor_agent_id,
            target_agent_id=r.target_agent_id,
            content=r.content,
            payload=r.payload,
            created_at=r.created_at,
        )
        for r in (rows[:limit] if limit is not None else rows)
    ]
