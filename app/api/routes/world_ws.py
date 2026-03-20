from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select

from app.persistence.engine import get_engine
from app.persistence.models import TickResult
from app.ws.broadcaster import world_broadcaster

router = APIRouter(tags=["world"])


@router.websocket("/ws/simulation")
async def simulation_socket(websocket: WebSocket, scenario_id: UUID | None = None) -> None:
    current_tick = 0
    if scenario_id is not None:
        with Session(get_engine()) as session:
            rows = list(
                session.exec(
                    select(TickResult)
                    .where(TickResult.scenario_id == scenario_id)
                    .order_by(TickResult.tick_number.desc())
                )
            )
            current_tick = rows[0].tick_number if rows else 0

    await world_broadcaster.connect(websocket, scenario_id, current_tick=current_tick)
    try:
        while True:
            payload = await websocket.receive_json()
            if scenario_id is not None:
                world_broadcaster.record_command(scenario_id, payload)
    except WebSocketDisconnect:
        world_broadcaster.disconnect(websocket)
