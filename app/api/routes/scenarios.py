from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.schemas.social import MessageRead
from app.api.deps import get_session
from app.persistence.models import DecisionLog, Relationship, Scenario, TickResult
from app.persistence.repositories.social_repository import SocialRepository
from app.persistence.repositories.scenario_repository import ScenarioRepository
from app.schemas.api import ScenarioCreate, ScenarioRead

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("", response_model=list[ScenarioRead])
def list_scenarios(session: Session = Depends(get_session)) -> list[ScenarioRead]:
    repo = ScenarioRepository(session)
    rows = repo.list_scenarios()
    return [ScenarioRead(id=r.id, name=r.name, status=r.status, current_tick=0) for r in rows]


@router.post("", response_model=ScenarioRead, status_code=201)
def create_scenario(payload: ScenarioCreate, session: Session = Depends(get_session)) -> ScenarioRead:
    repo = ScenarioRepository(session)
    row = repo.create_scenario(Scenario(name=payload.name, description=payload.description, status="ready"))
    return ScenarioRead(id=row.id, name=row.name, status=row.status, current_tick=0)


@router.get("/{scenario_id}", response_model=ScenarioRead)
def get_scenario(scenario_id: UUID, session: Session = Depends(get_session)) -> ScenarioRead:
    repo = ScenarioRepository(session)
    row = repo.get(scenario_id)
    if not row:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return ScenarioRead(id=row.id, name=row.name, status=row.status, current_tick=0)


@router.get("/{scenario_id}/messages", response_model=list[MessageRead])
def message_feed(
    scenario_id: UUID,
    agent_id: UUID | None = None,
    tick_from: int | None = None,
    tick_to: int | None = None,
    intent: str | None = None,
    session: Session = Depends(get_session),
) -> list[MessageRead]:
    repo = SocialRepository(session)
    rows = repo.list_messages(
        scenario_id=scenario_id,
        agent_id=agent_id,
        tick_from=tick_from,
        tick_to=tick_to,
        intent=intent,
    )
    return [
        MessageRead(
            id=row.id,
            scenario_id=row.scenario_id,
            tick_number=row.tick_number,
            sender_agent_id=row.sender_agent_id,
            receiver_agent_id=row.receiver_agent_id,
            target_mode=row.target_mode,
            content=row.content,
            intent=row.intent,
            emotional_tone=row.emotional_tone,
            intent_tags=row.intent_tags,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/{scenario_id}/compare/{other_scenario_id}")
def compare_runs(scenario_id: UUID, other_scenario_id: UUID, session: Session = Depends(get_session)) -> dict:
    base_ticks = list(session.exec(select(TickResult).where(TickResult.scenario_id == scenario_id)))
    other_ticks = list(session.exec(select(TickResult).where(TickResult.scenario_id == other_scenario_id)))
    base_decisions = list(session.exec(select(DecisionLog).where(DecisionLog.scenario_id == scenario_id)))
    other_decisions = list(session.exec(select(DecisionLog).where(DecisionLog.scenario_id == other_scenario_id)))
    base_relationships = list(session.exec(select(Relationship).where(Relationship.scenario_id == scenario_id)))
    other_relationships = list(session.exec(select(Relationship).where(Relationship.scenario_id == other_scenario_id)))

    return {
        "scenario_id_a": str(scenario_id),
        "scenario_id_b": str(other_scenario_id),
        "metrics": {
            "tick_count_delta": len(base_ticks) - len(other_ticks),
            "decision_count_delta": len(base_decisions) - len(other_decisions),
            "relationship_record_delta": len(base_relationships) - len(other_relationships),
        },
    }
