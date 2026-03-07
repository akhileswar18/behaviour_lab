from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.analytics.agent_analytics import AgentAnalyticsService
from app.api.deps import get_session
from app.api.schemas.analytics import AgentIdentityRead, AgentObservatoryRead

router = APIRouter(tags=["analytics"])


@router.get("/analytics/agents", response_model=list[AgentIdentityRead])
def list_agent_identities(session: Session = Depends(get_session)) -> list[AgentIdentityRead]:
    service = AgentAnalyticsService(session)
    return service.list_agent_identities()


@router.get("/analytics/agent-observatory", response_model=AgentObservatoryRead)
def get_agent_observatory(
    identity_key: str,
    scenario_id: UUID | None = None,
    tick_from: int | None = None,
    tick_to: int | None = None,
    zone_id: UUID | None = None,
    event_type: str | None = None,
    decision_source: str | None = None,
    session: Session = Depends(get_session),
) -> AgentObservatoryRead:
    service = AgentAnalyticsService(session)
    try:
        return service.build_agent_observatory(
            identity_key=identity_key,
            scenario_id=scenario_id,
            tick_from=tick_from,
            tick_to=tick_to,
            zone_id=zone_id,
            event_type=event_type,
            decision_source=decision_source,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/scenarios/{scenario_id}/analytics/agent/{agent_id}", response_model=AgentObservatoryRead)
def get_agent_analytics_compat(
    scenario_id: UUID,
    agent_id: UUID,
    tick_from: int | None = None,
    tick_to: int | None = None,
    zone_id: UUID | None = None,
    event_type: str | None = None,
    decision_source: str | None = None,
    session: Session = Depends(get_session),
) -> AgentObservatoryRead:
    service = AgentAnalyticsService(session)
    try:
        return service.build_agent_snapshot(
            scenario_id=scenario_id,
            agent_id=agent_id,
            tick_from=tick_from,
            tick_to=tick_to,
            zone_id=zone_id,
            event_type=event_type,
            decision_source=decision_source,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
