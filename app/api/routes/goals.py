from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_session
from app.api.schemas.social import GoalRead, IntentionRead
from app.persistence.repositories.planning_repository import PlanningRepository

router = APIRouter(prefix="/scenarios", tags=["goals"])


@router.get("/{scenario_id}/goals", response_model=list[GoalRead])
def get_goals(
    scenario_id: UUID,
    agent_id: UUID | None = None,
    session: Session = Depends(get_session),
) -> list[GoalRead]:
    repo = PlanningRepository(session)
    rows = repo.list_goals(scenario_id, agent_id=agent_id)
    return [
        GoalRead(
            id=row.id,
            scenario_id=row.scenario_id,
            agent_id=row.agent_id,
            goal_type=row.goal_type,
            priority=row.priority,
            status=row.status,
            target=row.target,
            source=row.source,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


@router.get("/{scenario_id}/intentions", response_model=list[IntentionRead])
def get_intentions(
    scenario_id: UUID,
    agent_id: UUID | None = None,
    session: Session = Depends(get_session),
) -> list[IntentionRead]:
    repo = PlanningRepository(session)
    rows = repo.list_intentions(scenario_id, agent_id=agent_id)
    return [
        IntentionRead(
            id=row.id,
            scenario_id=row.scenario_id,
            agent_id=row.agent_id,
            goal_id=row.goal_id,
            current_action_type=row.current_action_type,
            status=row.status,
            rationale=row.rationale,
            target_zone_id=row.target_zone_id,
            target_resource_id=row.target_resource_id,
            is_interruptible=row.is_interruptible,
            started_at=row.started_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]
