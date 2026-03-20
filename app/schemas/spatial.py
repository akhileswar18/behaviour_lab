from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TilePosition(BaseModel):
    tile_x: float
    tile_y: float
    subtile_progress: float | None = None


class NearbyAgent(BaseModel):
    agent_id: str
    agent_name: str
    tile_distance: int
    zone_name: str | None = None


class NearbyObject(BaseModel):
    object_id: str
    name: str
    zone_name: str | None = None
    affordance_type: str | None = None
    resource_type: str | None = None
    tile_position: TilePosition
    properties: dict[str, Any] = Field(default_factory=dict)


class PathResult(BaseModel):
    waypoints: list[TilePosition] = Field(default_factory=list)
    path_cost: int = 0
    target_zone_id: str | None = None
    target_object_id: str | None = None


class SpatialPerception(BaseModel):
    current_tile: TilePosition | None = None
    current_room: str | None = None
    zone_id: str | None = None
    nearby_agents: list[NearbyAgent] = Field(default_factory=list)
    nearby_objects: list[NearbyObject] = Field(default_factory=list)
    visible_resources: list[dict[str, Any]] = Field(default_factory=list)
    pathfinding_costs: dict[str, int] = Field(default_factory=dict)
    door_connections: list[str] = Field(default_factory=list)
