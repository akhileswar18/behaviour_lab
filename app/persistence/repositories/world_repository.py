from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from sqlmodel import Session, select

from app.persistence.models import Agent, AgentStateSnapshot, Resource, Zone
from app.persistence.repositories.base import RepositoryBase


class WorldRepository(RepositoryBase[Zone]):
    def __init__(self, session: Session):
        super().__init__(session)

    def list_zones(self, scenario_id: UUID) -> list[Zone]:
        statement = select(Zone).where(Zone.scenario_id == scenario_id).order_by(Zone.name)
        return list(self.session.exec(statement))

    def get_zone(self, zone_id: UUID) -> Zone | None:
        return self.session.get(Zone, zone_id)

    def list_resources(self, scenario_id: UUID, zone_id: UUID | None = None) -> list[Resource]:
        statement = select(Resource).where(Resource.scenario_id == scenario_id).order_by(Resource.resource_type)
        if zone_id is not None:
            statement = statement.where(Resource.zone_id == zone_id)
        return list(self.session.exec(statement))

    def get_resource(self, resource_id: UUID) -> Resource | None:
        return self.session.get(Resource, resource_id)

    def save_resource(self, resource: Resource) -> Resource:
        self.session.add(resource)
        self.session.commit()
        self.session.refresh(resource)
        return resource

    def latest_state(self, agent_id: UUID) -> AgentStateSnapshot | None:
        statement = (
            select(AgentStateSnapshot)
            .where(AgentStateSnapshot.agent_id == agent_id)
            .order_by(AgentStateSnapshot.tick_number.desc())
        )
        return self.session.exec(statement).first()

    def occupancy_by_zone(self, scenario_id: UUID) -> dict[UUID, list[UUID]]:
        agents = list(self.session.exec(select(Agent).where(Agent.scenario_id == scenario_id)))
        grouped: dict[UUID, list[UUID]] = defaultdict(list)
        for agent in agents:
            state = self.latest_state(agent.id)
            if state and state.zone_id is not None:
                grouped[state.zone_id].append(agent.id)
        return dict(grouped)

    def zone_lookup(self, scenario_id: UUID) -> dict[str, Zone]:
        return {zone.name: zone for zone in self.list_zones(scenario_id)}

    def occupancy_with_names(self, scenario_id: UUID) -> list[dict]:
        agents = {agent.id: agent for agent in self.session.exec(select(Agent).where(Agent.scenario_id == scenario_id))}
        occupancy = self.occupancy_by_zone(scenario_id)
        rows: list[dict] = []
        for zone in self.list_zones(scenario_id):
            rows.append(
                {
                    "zone_id": str(zone.id),
                    "zone_name": zone.name,
                    "zone_type": zone.zone_type,
                    "occupants": [
                        {"agent_id": str(agent_id), "agent_name": agents[agent_id].name}
                        for agent_id in occupancy.get(zone.id, [])
                        if agent_id in agents
                    ],
                }
            )
        return rows

    def resource_distribution(self, scenario_id: UUID, zone_id: UUID | None = None) -> list[dict]:
        return [
            {
                "resource_id": str(resource.id),
                "zone_id": str(resource.zone_id),
                "resource_type": resource.resource_type,
                "quantity": resource.quantity,
                "status": resource.status,
            }
            for resource in self.list_resources(scenario_id, zone_id=zone_id)
        ]
