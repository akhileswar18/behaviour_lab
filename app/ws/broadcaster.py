from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from fastapi import WebSocket

from app.api.schemas.world import ConnectionAckRead, WorldSnapshotRead


@dataclass(slots=True)
class Subscriber:
    websocket: WebSocket
    scenario_id: UUID | None


class WorldBroadcaster:
    def __init__(self) -> None:
        self._subscribers: list[Subscriber] = []
        self._loop: asyncio.AbstractEventLoop | None = None
        self.latest_snapshots: dict[UUID, WorldSnapshotRead] = {}
        self.command_log: dict[UUID, list[dict[str, object]]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, scenario_id: UUID | None, current_tick: int = 0) -> None:
        await websocket.accept()
        self._loop = asyncio.get_running_loop()
        self._subscribers.append(Subscriber(websocket=websocket, scenario_id=scenario_id))
        if scenario_id is not None:
            latest_tick = self.latest_snapshots.get(scenario_id).tick_number if scenario_id in self.latest_snapshots else current_tick
            await websocket.send_json(
                ConnectionAckRead(
                    scenario_id=str(scenario_id),
                    current_tick=latest_tick,
                    server_time=datetime.utcnow().isoformat(),
                ).model_dump()
            )

    def disconnect(self, websocket: WebSocket) -> None:
        self._subscribers = [item for item in self._subscribers if item.websocket is not websocket]

    async def _broadcast(self, snapshot: WorldSnapshotRead) -> None:
        stale: list[WebSocket] = []
        for subscriber in self._subscribers:
            if subscriber.scenario_id is not None and str(subscriber.scenario_id) != snapshot.scenario_id:
                continue
            try:
                await subscriber.websocket.send_json(snapshot.model_dump())
            except Exception:
                stale.append(subscriber.websocket)
        for websocket in stale:
            self.disconnect(websocket)

    def publish_snapshot(self, snapshot: WorldSnapshotRead) -> None:
        scenario_id = UUID(snapshot.scenario_id)
        self.latest_snapshots[scenario_id] = snapshot
        if self._loop is not None and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast(snapshot), self._loop)

    def record_command(self, scenario_id: UUID, payload: dict[str, object]) -> None:
        self.command_log[scenario_id].append(payload)


world_broadcaster = WorldBroadcaster()
