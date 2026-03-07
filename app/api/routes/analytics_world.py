from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.analytics.world_analytics import WorldAnalyticsService
from app.api.deps import get_session
from app.api.schemas.analytics import WorldAnalyticsRead

router = APIRouter(prefix="/scenarios", tags=["analytics"])


@router.get("/{scenario_id}/analytics/world", response_model=WorldAnalyticsRead)
def get_world_analytics(
    scenario_id: UUID,
    tick_from: int | None = None,
    tick_to: int | None = None,
    agent_id: UUID | None = None,
    zone_id: UUID | None = None,
    event_type: str | None = None,
    session: Session = Depends(get_session),
) -> WorldAnalyticsRead:
    service = WorldAnalyticsService(session)
    return service.build_snapshot(
        scenario_id=scenario_id,
        tick_from=tick_from,
        tick_to=tick_to,
        agent_id=agent_id,
        zone_id=zone_id,
        event_type=event_type,
    )
