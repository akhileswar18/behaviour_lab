# Tilemap Format Contract

## Purpose

This contract defines the Tiled JSON structure the embodied-world client expects for the
visual-quality fix. The backend remains authoritative for simulation state, but the renderer
and backend-compatible map loader must agree on map shape, layer naming, collision semantics,
and zone metadata.

## File Locations

- Primary client asset: `client/public/assets/maps/house.json`
- Shared backend-compatible copy when needed: `maps/house.json`

## Required Map Metadata

| Field | Required Value |
|-------|----------------|
| `type` | `map` |
| `orientation` | `orthogonal` |
| `tilewidth` | `16` |
| `tileheight` | `16` |
| `width` | `40` |
| `height` | `30` |

## Required Layer Set

The Tiled JSON must contain the following layers by exact name:

| Layer Name | Layer Type | Purpose |
|------------|------------|---------|
| `floor` | Tile layer | Base floors for each room and corridor |
| `walls` | Tile layer | Visible walls and structural separators |
| `furniture` | Tile layer | Furniture tiles that render below upper decor |
| `furniture_upper` | Tile layer | Tall furniture tiles that render above agents |
| `collision` | Tile layer | Non-walkable blocked space aligned to the visual map |
| `objects` | Object layer | Zone rectangles and other semantic metadata |

## Tileset Requirements

- The map references an external tileset image rather than embedded image data.
- The client loads the tileset image separately as `interiors.png`.
- Tileset naming in Tiled must match the tileset image name used by `map.addTilesetImage(...)`.
- The tileset must be compatible with 16x16 native tiles.

## Zone Object Requirements

The `objects` layer must define rectangle objects for rooms or semantic areas.

Required custom property:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `zone` | string | Yes | Backend-compatible zone identifier |

Allowed `zone` values for this feature:

- `kitchen`
- `bedroom`
- `living_room`
- `bathroom`
- `commons`

Zone rules:

- zone names must match existing embodied-world expectations exactly
- rectangles must align with the intended room footprint
- door openings should be excluded from blocked collision geometry where movement is allowed

## Collision Semantics

- Any non-empty tile in `collision` is treated as blocked by the renderer and must align with
  backend walkability semantics.
- Walls and the solid footprint of furniture should be represented in `collision`.
- Decorative or overhead-only visuals should not block movement unless the backend is also
  expected to treat them as non-walkable.

## Renderer Consumption

`Preloader.ts` must:

- load `house.json` with a stable key such as `world-map`
- load `interiors.png` before `WorldScene` creates the map

`WorldScene.ts` must:

- create the tilemap with `this.make.tilemap({ key: "world-map" })`
- bind the loaded tileset with `map.addTilesetImage(...)`
- create visual layers in the order `floor`, `walls`, `furniture`, `furniture_upper`
- build renderer collision awareness from the `collision` layer

## Fallback Rules

- If `house.json` fails to load, the client may fall back to the current debug rectangle room
  layout and log a warning.
- If the tileset image fails to load, the client may fall back to placeholder room geometry
  rather than failing to render the scene entirely.
- If a scenario is still zone-only, the rectangle fallback remains an acceptable degraded mode.
