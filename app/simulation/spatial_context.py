from __future__ import annotations

from uuid import UUID

from app.persistence.models import Agent, AgentStateSnapshot, Resource, Zone
from app.schemas.spatial import NearbyAgent, NearbyObject, SpatialPerception, TilePosition
from app.simulation.pathfinding import astar_path
from app.simulation.tilemap_loader import ParsedTileMap


def resolve_tile_position(
    state: AgentStateSnapshot | None,
    zone: Zone | None,
    tilemap: ParsedTileMap | None,
) -> tuple[int, int] | None:
    if state and state.tile_x is not None and state.tile_y is not None:
        return state.tile_x, state.tile_y
    if zone is None or tilemap is None:
        return None
    return tilemap.center_for_zone(zone.name)


def build_spatial_perception(
    *,
    agent: Agent,
    state: AgentStateSnapshot | None,
    zone: Zone | None,
    tilemap: ParsedTileMap | None,
    latest_state_by_agent: dict[UUID, AgentStateSnapshot | None],
    agents_by_id: dict[UUID, Agent],
    zones_by_id: dict[UUID, Zone],
    resources: list[Resource],
    radius: int = 4,
) -> SpatialPerception:
    tile_position = resolve_tile_position(state, zone, tilemap)
    if tile_position is None:
        return SpatialPerception(zone_id=str(zone.id) if zone else None)

    tile_x, tile_y = tile_position
    current_room = tilemap.zone_for_tile(tile_x, tile_y) if tilemap else zone.name if zone else None

    nearby_agents: list[NearbyAgent] = []
    if tilemap is not None:
        for candidate_id, candidate_state in latest_state_by_agent.items():
            if candidate_id == agent.id or candidate_state is None:
                continue
            candidate_agent = agents_by_id.get(candidate_id)
            candidate_zone = zones_by_id.get(candidate_state.zone_id) if candidate_state.zone_id else None
            candidate_position = resolve_tile_position(candidate_state, candidate_zone, tilemap)
            if candidate_agent is None or candidate_position is None:
                continue
            distance = abs(candidate_position[0] - tile_x) + abs(candidate_position[1] - tile_y)
            if distance <= radius:
                nearby_agents.append(
                    NearbyAgent(
                        agent_id=str(candidate_id),
                        agent_name=candidate_agent.name,
                        tile_distance=distance,
                        zone_name=candidate_zone.name if candidate_zone else None,
                    )
                )

    nearby_objects: list[NearbyObject] = []
    door_connections: list[str] = []
    if tilemap is not None:
        for item in tilemap.objects:
            if item.object_type == "zone":
                continue
            distance = abs(item.tile_x - tile_x) + abs(item.tile_y - tile_y)
            if distance <= radius or (item.zone_name and item.zone_name == current_room):
                nearby_objects.append(
                    NearbyObject(
                        object_id=item.object_id,
                        name=item.name,
                        zone_name=item.zone_name,
                        affordance_type=item.properties.get("affordance_type"),
                        resource_type=item.properties.get("resource_type"),
                        tile_position=TilePosition(tile_x=item.tile_x, tile_y=item.tile_y),
                        properties=item.properties,
                    )
                )
            if item.properties.get("door"):
                door_connections.append(item.name)

    visible_resources: list[dict[str, object]] = []
    pathfinding_costs: dict[str, int] = {}
    if zone is not None:
        for resource in resources:
            resource_zone = zones_by_id.get(resource.zone_id)
            if resource_zone is None:
                continue
            if resource_zone.id == zone.id:
                visible_resources.append(
                    {
                        "resource_id": str(resource.id),
                        "resource_type": resource.resource_type,
                        "quantity": resource.quantity,
                        "zone_name": resource_zone.name,
                    }
                )
            if tilemap is not None:
                target_center = tilemap.center_for_zone(resource_zone.name)
                if target_center is None:
                    continue
                path = astar_path(tilemap.collision_grid, (tile_x, tile_y), target_center)
                if path:
                    pathfinding_costs[f"{resource_zone.name}:{resource.resource_type}"] = max(len(path) - 1, 0)

    return SpatialPerception(
        current_tile=TilePosition(tile_x=tile_x, tile_y=tile_y),
        current_room=current_room,
        zone_id=str(zone.id) if zone else None,
        nearby_agents=nearby_agents,
        nearby_objects=nearby_objects,
        visible_resources=visible_resources,
        pathfinding_costs=pathfinding_costs,
        door_connections=door_connections,
    )
