from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.persistence.models import (
    Agent,
    AgentStateSnapshot,
    DecisionLog,
    Goal,
    Message,
    Resource,
    SimulationEvent,
    TileMapConfig,
    TickResult,
    Zone,
)
from app.persistence.repositories.spatial_repository import SpatialRepository
from app.schemas.social import SimulationEventType
from app.schemas.spatial import PathResult, SpatialPerception, TilePosition
from app.simulation.spatial_context import build_spatial_perception
from app.simulation.tilemap_loader import ParsedTileMap, default_tilemap_path, load_tilemap


class BubbleRead(BaseModel):
    content: str
    tone: str | None = None


class GoalSummaryRead(BaseModel):
    goal_type: str
    priority: float


class DecisionSummaryRead(BaseModel):
    tick_number: int
    action: str
    rationale: str


class NeedsRead(BaseModel):
    hunger: float
    safety_need: float
    social_need: float
    energy: float | None = None
    stress: float | None = None


class AgentWorldRead(BaseModel):
    agent_id: str
    name: str
    zone_id: str | None = None
    zone_name: str | None = None
    position: TilePosition | None = None
    target: TilePosition | None = None
    path: PathResult | None = None
    mood: str
    emoji: str | None = None
    action: str
    speech: BubbleRead | None = None
    thought: BubbleRead | None = None
    needs: NeedsRead
    goal: GoalSummaryRead | None = None
    recent_decisions: list[DecisionSummaryRead] = Field(default_factory=list)
    spatial_context: SpatialPerception | None = None


class ConversationRead(BaseModel):
    source_agent_id: str
    target_agent_id: str | None = None
    intent: str
    tone: str
    content: str


class WorldEventRead(BaseModel):
    event_id: str | None = None
    event_type: str
    content: str
    created_at: str | None = None


class WorldSnapshotRead(BaseModel):
    schema_version: str = "1.0"
    type: str = "tick_update"
    scenario_id: str
    tick_number: int
    sim_time: str
    time_of_day: str
    agents: list[AgentWorldRead] = Field(default_factory=list)
    conversations: list[ConversationRead] = Field(default_factory=list)
    world_events: list[WorldEventRead] = Field(default_factory=list)


class ConnectionAckRead(BaseModel):
    schema_version: str = "1.0"
    type: str = "connection_ack"
    scenario_id: str
    current_tick: int
    server_time: str


class ReplayResponseRead(BaseModel):
    scenario_id: str
    tick_start: int
    tick_end: int
    snapshots: list[WorldSnapshotRead] = Field(default_factory=list)


class WorldMapRead(BaseModel):
    scenario_id: str | None = None
    map_file_path: str
    map: dict[str, Any]


def _time_of_day(tick_number: int) -> str:
    phases = ["dawn", "day", "evening", "night"]
    return phases[tick_number % len(phases)]


def _action_emoji(action: str) -> str:
    return {
        "move": "🚶",
        "acquire_resource": "📦",
        "consume_resource": "🍽️",
        "warn": "⚠️",
        "cooperate": "🤝",
        "propose": "💬",
        "observe": "👀",
        "wait": "⏳",
    }.get(action, "🙂")


def load_tilemap_for_scenario(session: Session, scenario_id: UUID | None) -> tuple[TileMapConfig | None, ParsedTileMap]:
    config = None
    if scenario_id is not None:
        config = SpatialRepository(session).get_map_config(scenario_id)
    map_path = config.map_file_path if config else default_tilemap_path()
    return config, load_tilemap(map_path)


def _latest_states(session: Session, scenario_id: UUID, tick_number: int) -> dict[UUID, AgentStateSnapshot | None]:
    repo = SpatialRepository(session)
    return repo.latest_states_for_scenario(scenario_id, tick_number=tick_number)


def build_world_snapshot(session: Session, scenario_id: UUID, tick_number: int) -> WorldSnapshotRead:
    _, tilemap = load_tilemap_for_scenario(session, scenario_id)
    agents = list(session.exec(select(Agent).where(Agent.scenario_id == scenario_id).order_by(Agent.name)))
    agents_by_id = {agent.id: agent for agent in agents}
    zones = {
        zone.id: zone
        for zone in session.exec(select(Zone).where(Zone.scenario_id == scenario_id).order_by(Zone.name))
    }
    latest_state_by_agent = _latest_states(session, scenario_id, tick_number)
    resources = list(session.exec(select(Resource).where(Resource.scenario_id == scenario_id).order_by(Resource.resource_type)))
    decisions = list(
        session.exec(
            select(DecisionLog)
            .where(DecisionLog.scenario_id == scenario_id)
            .where(DecisionLog.tick_number <= tick_number)
            .order_by(DecisionLog.tick_number.desc(), DecisionLog.created_at.desc())
        )
    )
    decisions_by_agent: dict[UUID, list[DecisionLog]] = {}
    for row in decisions:
        decisions_by_agent.setdefault(row.agent_id, [])
        if len(decisions_by_agent[row.agent_id]) < 3:
            decisions_by_agent[row.agent_id].append(row)

    message_rows = list(
        session.exec(
            select(Message)
            .where(Message.scenario_id == scenario_id)
            .where(Message.tick_number == tick_number)
            .order_by(Message.created_at)
        )
    )
    events = list(
        session.exec(
            select(SimulationEvent)
            .where(SimulationEvent.scenario_id == scenario_id)
            .where(SimulationEvent.tick_number == tick_number)
            .order_by(SimulationEvent.created_at)
        )
    )
    active_goals = {
        goal.agent_id: goal
        for goal in session.exec(select(Goal).where(Goal.scenario_id == scenario_id).where(Goal.status == "active"))
    }

    world_agents: list[AgentWorldRead] = []
    for agent in agents:
        state = latest_state_by_agent.get(agent.id)
        zone = zones.get(state.zone_id) if state and state.zone_id else None
        spatial_context = build_spatial_perception(
            agent=agent,
            state=state,
            zone=zone,
            tilemap=tilemap,
            latest_state_by_agent=latest_state_by_agent,
            agents_by_id=agents_by_id,
            zones_by_id=zones,
            resources=resources,
        )
        decision_rows = decisions_by_agent.get(agent.id, [])
        latest_decision = decision_rows[0] if decision_rows else None
        latest_move = next(
            (
                event
                for event in events
                if event.actor_agent_id == agent.id and event.event_type == SimulationEventType.MOVE.value
            ),
            None,
        )
        payload = latest_move.payload if latest_move else {}
        path_waypoints = [
            TilePosition(tile_x=item["tile_x"], tile_y=item["tile_y"])
            for item in payload.get("path", [])
            if isinstance(item, dict) and "tile_x" in item and "tile_y" in item
        ]
        current_tile = None
        if state and state.tile_x is not None and state.tile_y is not None:
            current_tile = TilePosition(tile_x=state.tile_x, tile_y=state.tile_y)
        elif zone is not None:
            center = tilemap.center_for_zone(zone.name)
            if center is not None:
                current_tile = TilePosition(tile_x=center[0], tile_y=center[1])
        speech = next((row for row in message_rows if row.sender_agent_id == agent.id), None)
        goal = active_goals.get(agent.id)
        world_agents.append(
            AgentWorldRead(
                agent_id=str(agent.id),
                name=agent.name,
                zone_id=str(zone.id) if zone else None,
                zone_name=zone.name if zone else None,
                position=current_tile,
                target=(
                    TilePosition(tile_x=payload["target_tile_x"], tile_y=payload["target_tile_y"])
                    if payload.get("target_tile_x") is not None and payload.get("target_tile_y") is not None
                    else None
                ),
                path=(
                    PathResult(
                        waypoints=path_waypoints,
                        path_cost=max(len(path_waypoints) - 1, 0),
                        target_zone_id=str(payload["target_zone_id"]) if payload.get("target_zone_id") else None,
                    )
                    if path_waypoints
                    else None
                ),
                mood=state.mood if state else "neutral",
                emoji=_action_emoji(latest_decision.selected_action if latest_decision else "observe"),
                action=latest_decision.selected_action if latest_decision else "observe",
                speech=BubbleRead(content=speech.content, tone=speech.emotional_tone) if speech else None,
                thought=BubbleRead(content=latest_decision.rationale) if latest_decision else None,
                needs=NeedsRead(
                    hunger=state.hunger if state else 0.0,
                    safety_need=state.safety_need if state else 0.0,
                    social_need=state.social_need if state else 0.0,
                    energy=state.energy if state else 100.0,
                    stress=state.stress if state else 0.0,
                ),
                goal=(
                    GoalSummaryRead(goal_type=goal.goal_type, priority=goal.priority)
                    if goal is not None
                    else None
                ),
                recent_decisions=[
                    DecisionSummaryRead(
                        tick_number=item.tick_number,
                        action=item.selected_action,
                        rationale=item.rationale,
                    )
                    for item in decision_rows
                ],
                spatial_context=spatial_context,
            )
        )

    return WorldSnapshotRead(
        scenario_id=str(scenario_id),
        tick_number=tick_number,
        sim_time=datetime.utcnow().isoformat(),
        time_of_day=_time_of_day(tick_number),
        agents=world_agents,
        conversations=[
            ConversationRead(
                source_agent_id=str(row.sender_agent_id),
                target_agent_id=str(row.receiver_agent_id) if row.receiver_agent_id else None,
                intent=row.intent,
                tone=row.emotional_tone,
                content=row.content,
            )
            for row in message_rows
        ],
        world_events=[
            WorldEventRead(
                event_id=str(event.id),
                event_type=event.event_type,
                content=event.content,
                created_at=event.created_at.isoformat(),
            )
            for event in events
        ],
    )


def build_replay_payload(session: Session, scenario_id: UUID, tick_start: int, tick_end: int) -> ReplayResponseRead:
    tick_numbers = list(
        session.exec(
            select(TickResult.tick_number)
            .where(TickResult.scenario_id == scenario_id)
            .where(TickResult.tick_number >= tick_start)
            .where(TickResult.tick_number <= tick_end)
            .order_by(TickResult.tick_number.asc())
        )
    )
    if not tick_numbers:
        raise ValueError("No stored snapshots in requested tick range")

    snapshots = [build_world_snapshot(session, scenario_id, tick_number) for tick_number in tick_numbers]
    return ReplayResponseRead(
        scenario_id=str(scenario_id),
        tick_start=tick_numbers[0],
        tick_end=tick_numbers[-1],
        snapshots=snapshots,
    )
