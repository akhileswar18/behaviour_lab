from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_session
from app.api.schemas.world import ReplayResponseRead, WorldMapRead, build_replay_payload, load_tilemap_for_scenario
from app.persistence.models import Scenario

router = APIRouter(prefix="/api/world", tags=["world"])


@router.get("/map", response_model=WorldMapRead)
def get_world_map(
    scenario_id: UUID | None = None,
    session: Session = Depends(get_session),
) -> WorldMapRead:
    if scenario_id is not None and session.get(Scenario, scenario_id) is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    _, tilemap = load_tilemap_for_scenario(session, scenario_id)
    return WorldMapRead(
        scenario_id=str(scenario_id) if scenario_id else None,
        map_file_path=tilemap.map_file_path,
        map=tilemap.raw_map,
    )


@router.get("/replay/{tick_start}/{tick_end}", response_model=ReplayResponseRead)
def get_replay_range(
    tick_start: int,
    tick_end: int,
    scenario_id: UUID,
    session: Session = Depends(get_session),
) -> ReplayResponseRead:
    if session.get(Scenario, scenario_id) is None:
        raise HTTPException(status_code=404, detail="Scenario not found")
    if tick_end < tick_start:
        raise HTTPException(status_code=400, detail="tick_end must be >= tick_start")
    try:
        return build_replay_payload(session, scenario_id, tick_start, tick_end)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
