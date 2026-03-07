from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from app.api.schemas.analytics import (
    ResourceDistributionRead,
    WorldAnalyticsRead,
    WorldMetricsRead,
    WorldStateSummaryRead,
    ZoneOccupancyRead,
)
from app.persistence.models import Agent, Relationship, TickResult
from app.persistence.repositories.planning_repository import PlanningRepository
from app.persistence.repositories.social_repository import SocialRepository
from app.persistence.repositories.world_repository import WorldRepository


def average_trust(relationships: list[Relationship]) -> float:
    if not relationships:
        return 0.0
    return round(sum(item.trust for item in relationships) / len(relationships), 3)


def goal_completion_rate(statuses: list[str]) -> float:
    if not statuses:
        return 0.0
    completed = sum(1 for status in statuses if status == "completed")
    return round(completed / len(statuses), 3)


def movement_frequency(move_count: int, tick_span: int) -> float:
    if tick_span <= 0:
        return 0.0
    return round(move_count / tick_span, 3)


def resource_scarcity(resources: list[dict]) -> float:
    if not resources:
        return 0.0
    scarce = sum(1 for item in resources if int(item.get("quantity", 0)) <= 0 or item.get("status") == "depleted")
    return round(scarce / len(resources), 3)


class WorldAnalyticsService:
    def __init__(self, session: Session):
        self.session = session
        self.social_repo = SocialRepository(session)
        self.world_repo = WorldRepository(session)
        self.planning_repo = PlanningRepository(session)

    def build_snapshot(
        self,
        scenario_id: UUID,
        tick_from: int | None = None,
        tick_to: int | None = None,
        zone_id: UUID | None = None,
        event_type: str | None = None,
        agent_id: UUID | None = None,
    ) -> WorldAnalyticsRead:
        zones = self.world_repo.list_zones(scenario_id)
        occupancy = self.world_repo.occupancy_with_names(scenario_id)
        resources = self.world_repo.resource_distribution(scenario_id, zone_id=zone_id)
        agents = list(self.session.exec(select(Agent).where(Agent.scenario_id == scenario_id)))
        relationships = self.social_repo.list_relationships(scenario_id, agent_id=agent_id)
        timeline = self.social_repo.list_timeline(
            scenario_id=scenario_id,
            tick_from=tick_from,
            tick_to=tick_to,
            agent_id=agent_id,
            event_type=event_type,
            zone_id=zone_id,
        )
        tick_rows = list(self.session.exec(select(TickResult).where(TickResult.scenario_id == scenario_id)))
        current_tick = max((row.tick_number for row in tick_rows), default=0)
        tick_values = [event.tick_number for event in timeline]
        tick_span = (max(tick_values) - min(tick_values) + 1) if tick_values else max(current_tick, 1)
        goals = self.planning_repo.list_goals(scenario_id, agent_id=agent_id)

        if zone_id is not None:
            occupancy = [row for row in occupancy if row["zone_id"] == str(zone_id)]
            zones = [zone for zone in zones if zone.id == zone_id]

        zone_lookup = {str(zone.id): zone.name for zone in zones}
        zone_occupancy = [
            ZoneOccupancyRead(
                zone_id=UUID(row["zone_id"]),
                zone_name=row["zone_name"],
                zone_type=row["zone_type"],
                occupant_count=len(row["occupants"]),
                occupants=row["occupants"],
                resource_types=[item["resource_type"] for item in resources if item["zone_id"] == row["zone_id"]],
            )
            for row in occupancy
        ]
        resource_distribution = [
            ResourceDistributionRead(
                resource_id=UUID(row["resource_id"]),
                zone_id=UUID(row["zone_id"]),
                zone_name=zone_lookup.get(row["zone_id"]),
                resource_type=row["resource_type"],
                quantity=row["quantity"],
                status=row["status"],
            )
            for row in resources
        ]

        move_count = sum(1 for event in timeline if event.event_type == "move")
        global_event_feed = [
            {
                "id": str(event.id),
                "tick_number": event.tick_number,
                "event_type": event.event_type,
                "content": event.content,
                "payload": event.payload,
                "created_at": event.created_at.isoformat(),
            }
            for event in timeline[:25]
        ]

        return WorldAnalyticsRead(
            scenario_id=scenario_id,
            current_tick=current_tick,
            world_state=WorldStateSummaryRead(
                zone_count=len(zones),
                agent_count=len(agents) if agent_id is None else 1,
                resource_unit_count=sum(row["quantity"] for row in resources),
                active_tick_span=tick_span,
            ),
            global_event_feed=global_event_feed,
            zone_occupancy=zone_occupancy,
            resource_distribution=resource_distribution,
            metrics=WorldMetricsRead(
                average_trust=average_trust(relationships),
                goal_completion_rate=goal_completion_rate([goal.status for goal in goals]),
                movement_frequency=movement_frequency(move_count, tick_span),
                resource_scarcity=resource_scarcity(resources),
            ),
        )
