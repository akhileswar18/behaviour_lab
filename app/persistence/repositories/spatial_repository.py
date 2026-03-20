from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Agent, AgentStateSnapshot, TileMapConfig
from app.persistence.repositories.base import RepositoryBase


class SpatialRepository(RepositoryBase[TileMapConfig]):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_map_config(self, scenario_id: UUID) -> TileMapConfig | None:
        statement = select(TileMapConfig).where(TileMapConfig.scenario_id == scenario_id)
        return self.session.exec(statement).first()

    def save_map_config(self, row: TileMapConfig) -> TileMapConfig:
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def latest_states_for_scenario(
        self,
        scenario_id: UUID,
        tick_number: int | None = None,
    ) -> dict[UUID, AgentStateSnapshot | None]:
        agents = list(self.session.exec(select(Agent).where(Agent.scenario_id == scenario_id)))
        states: dict[UUID, AgentStateSnapshot | None] = {}
        for agent in agents:
            statement = (
                select(AgentStateSnapshot)
                .where(AgentStateSnapshot.agent_id == agent.id)
                .order_by(AgentStateSnapshot.tick_number.desc())
            )
            if tick_number is not None:
                statement = statement.where(AgentStateSnapshot.tick_number <= tick_number)
            states[agent.id] = self.session.exec(statement).first()
        return states

    def states_in_zone(
        self,
        scenario_id: UUID,
        zone_id: UUID,
        tick_number: int | None = None,
    ) -> list[AgentStateSnapshot]:
        states = self.latest_states_for_scenario(scenario_id, tick_number=tick_number)
        return [
            state
            for state in states.values()
            if state is not None and state.zone_id == zone_id
        ]

    def states_near_tile(
        self,
        scenario_id: UUID,
        tile_x: int,
        tile_y: int,
        radius: int,
        tick_number: int | None = None,
    ) -> list[AgentStateSnapshot]:
        states = self.latest_states_for_scenario(scenario_id, tick_number=tick_number)
        nearby: list[AgentStateSnapshot] = []
        for state in states.values():
            if state is None or state.tile_x is None or state.tile_y is None:
                continue
            distance = abs(state.tile_x - tile_x) + abs(state.tile_y - tile_y)
            if distance <= radius:
                nearby.append(state)
        return nearby
