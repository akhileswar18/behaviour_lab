from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ZoneRegion:
    name: str
    zone_name: str
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def contains(self, tile_x: int, tile_y: int) -> bool:
        return self.x <= tile_x < (self.x + self.width) and self.y <= tile_y < (self.y + self.height)


@dataclass(slots=True)
class MapObject:
    object_id: str
    name: str
    object_type: str
    zone_name: str | None
    tile_x: int
    tile_y: int
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ParsedTileMap:
    map_file_path: str
    tile_width: int
    tile_height: int
    grid_width: int
    grid_height: int
    raw_map: dict[str, Any]
    layers: dict[str, dict[str, Any]]
    collision_grid: list[list[bool]]
    zones: dict[str, ZoneRegion]
    objects: list[MapObject]

    def center_for_zone(self, zone_name: str) -> tuple[int, int] | None:
        region = self.zones.get(zone_name)
        if region is None:
            return None
        return region.center

    def zone_for_tile(self, tile_x: int, tile_y: int) -> str | None:
        for zone_name, region in self.zones.items():
            if region.contains(tile_x, tile_y):
                return zone_name
        return None


def _properties_to_dict(properties: list[dict[str, Any]] | None) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in properties or []:
        name = item.get("name")
        if name:
            result[str(name)] = item.get("value")
    return result


def default_tilemap_path() -> Path:
    return Path(__file__).resolve().parents[2] / "maps" / "house.json"


def _normalize_path(path: str | Path | None) -> Path:
    if path is None:
        return default_tilemap_path()
    return Path(path).resolve()


def _reshape_layer(data: list[int], width: int, height: int) -> list[list[int]]:
    padded = list(data[: width * height])
    if len(padded) < width * height:
        padded.extend([0] * (width * height - len(padded)))
    return [padded[index : index + width] for index in range(0, width * height, width)]


def load_tilemap(path: str | Path | None = None) -> ParsedTileMap:
    map_path = _normalize_path(path)
    raw_map = json.loads(map_path.read_text(encoding="utf-8"))
    tile_width = int(raw_map.get("tilewidth", 16))
    tile_height = int(raw_map.get("tileheight", 16))
    grid_width = int(raw_map.get("width", 0))
    grid_height = int(raw_map.get("height", 0))

    layers_by_name: dict[str, dict[str, Any]] = {}
    collision_grid = [[False for _ in range(grid_width)] for _ in range(grid_height)]
    zones: dict[str, ZoneRegion] = {}
    objects: list[MapObject] = []

    for layer in raw_map.get("layers", []):
        layer_name = str(layer.get("name", ""))
        layers_by_name[layer_name] = layer
        if layer_name == "collision" and layer.get("type") == "tilelayer":
            rows = _reshape_layer(list(layer.get("data", [])), grid_width, grid_height)
            collision_grid = [[cell != 0 for cell in row] for row in rows]
        if layer_name == "objects" and layer.get("type") == "objectgroup":
            for item in layer.get("objects", []):
                props = _properties_to_dict(item.get("properties"))
                tile_x = int(float(item.get("x", 0)) // tile_width)
                tile_y = int(float(item.get("y", 0)) // tile_height)
                width = max(1, int(float(item.get("width", tile_width)) // tile_width))
                height = max(1, int(float(item.get("height", tile_height)) // tile_height))
                zone_name = props.get("zone")
                object_type = str(item.get("type", "object"))
                if zone_name and object_type == "zone":
                    zones[str(zone_name)] = ZoneRegion(
                        name=str(item.get("name", zone_name)),
                        zone_name=str(zone_name),
                        x=tile_x,
                        y=tile_y,
                        width=width,
                        height=height,
                    )
                objects.append(
                    MapObject(
                        object_id=str(item.get("id")),
                        name=str(item.get("name", object_type)),
                        object_type=object_type,
                        zone_name=str(zone_name) if zone_name else None,
                        tile_x=tile_x,
                        tile_y=tile_y,
                        properties=props,
                    )
                )

    required_layers = {"floor", "walls", "furniture", "collision", "objects"}
    missing = required_layers - set(layers_by_name)
    if missing:
        raise ValueError(f"Tilemap missing required layers: {sorted(missing)}")
    if not zones:
        raise ValueError("Tilemap must declare at least one zone mapping in the objects layer")

    return ParsedTileMap(
        map_file_path=str(map_path),
        tile_width=tile_width,
        tile_height=tile_height,
        grid_width=grid_width,
        grid_height=grid_height,
        raw_map=raw_map,
        layers=layers_by_name,
        collision_grid=collision_grid,
        zones=zones,
        objects=objects,
    )
