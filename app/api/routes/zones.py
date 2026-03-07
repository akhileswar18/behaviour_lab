from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_session
from app.api.schemas.social import ZoneRead
from app.persistence.repositories.world_repository import WorldRepository

router = APIRouter(prefix="/scenarios", tags=["zones"])


@router.get("/{scenario_id}/zones", response_model=list[ZoneRead])
def get_zones(scenario_id: UUID, session: Session = Depends(get_session)) -> list[ZoneRead]:
    repo = WorldRepository(session)
    zones = repo.list_zones(scenario_id)
    occupancy = repo.occupancy_by_zone(scenario_id)
    occupancy_rows = {row["zone_id"]: row["occupants"] for row in repo.occupancy_with_names(scenario_id)}
    resources_by_zone: dict[UUID, list[str]] = {}
    for resource in repo.list_resources(scenario_id):
        resources_by_zone.setdefault(resource.zone_id, []).append(resource.resource_type)
    return [
        ZoneRead(
            id=zone.id,
            scenario_id=zone.scenario_id,
            name=zone.name,
            zone_type=zone.zone_type,
            metadata=zone.zone_metadata,
            occupant_ids=occupancy.get(zone.id, []),
            occupant_names=[row["agent_name"] for row in occupancy_rows.get(str(zone.id), [])],
            occupant_count=len(occupancy.get(zone.id, [])),
            resource_types=resources_by_zone.get(zone.id, []),
            resource_count=len(resources_by_zone.get(zone.id, [])),
        )
        for zone in zones
    ]
