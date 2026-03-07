from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_session
from app.api.schemas.social import ResourceRead
from app.persistence.repositories.world_repository import WorldRepository

router = APIRouter(prefix="/scenarios", tags=["resources"])


@router.get("/{scenario_id}/resources", response_model=list[ResourceRead])
def get_resources(
    scenario_id: UUID,
    zone_id: UUID | None = None,
    session: Session = Depends(get_session),
) -> list[ResourceRead]:
    repo = WorldRepository(session)
    rows = repo.list_resources(scenario_id, zone_id=zone_id)
    zone_lookup = {str(zone.id): zone.name for zone in repo.list_zones(scenario_id)}
    return [
        ResourceRead(
            id=row.id,
            scenario_id=row.scenario_id,
            zone_id=row.zone_id,
            zone_name=zone_lookup.get(str(row.zone_id)),
            resource_type=row.resource_type,
            quantity=row.quantity,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]
