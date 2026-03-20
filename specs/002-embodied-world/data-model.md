# Data Model: Phase 5 2D Embodied Simulation World

## Scope

Phase 5 extends the existing zone-based world with optional tile-based spatial grounding,
real-time world snapshots, and replay contracts. Existing dashboard and simulation entities
remain valid.

## New/Extended Entities

### AgentStateSnapshot (extended persisted entity)

- Purpose: store an agent's authoritative state for one tick, now including optional spatial
  coordinates.
- New fields:
  - `tile_x: int | None`
  - `tile_y: int | None`
- Existing fields retained:
  - `zone_id`, mood, active goals, energy, stress, hunger, safety need, social need,
    inventory, beliefs, tick number
- Validation:
  - `tile_x` and `tile_y` MUST both be null for zone-only scenarios
  - `tile_x` and `tile_y` MUST both be present for embodied scenarios once placement begins
  - coordinates MUST fall within the loaded tilemap grid bounds

### TileMapConfig (new persisted entity)

- Purpose: bind a scenario to a shared tilemap and expose map metadata needed by backend and
  renderer.
- Fields:
  - `id`
  - `scenario_id`
  - `map_file_path`
  - `tile_width`
  - `tile_height`
  - `grid_width`
  - `grid_height`
  - `zone_bindings` (JSON: room/zone mapping)
  - `created_at`
- Validation:
  - `map_file_path` MUST resolve to a repository-managed Tiled JSON file
  - dimensions MUST match the parsed map metadata
  - `zone_bindings` MUST reference existing scenario zones

### TilePosition (shared schema)

- Purpose: represent an authoritative tile coordinate for transport and decision context.
- Fields:
  - `tile_x`
  - `tile_y`
  - `subtile_progress` (optional, transport-only, for interpolation hints)
- Validation:
  - `tile_x` and `tile_y` MUST be integers on the backend contract
  - transport payloads MAY include interpolation hints but MUST preserve the current
    authoritative tile

### SpatialPerception (ephemeral decision-context schema)

- Purpose: add embodied context to the decision engine for one agent at one tick.
- Fields:
  - `current_tile`
  - `current_room`
  - `zone_id`
  - `nearby_agents`
  - `nearby_objects`
  - `visible_resources`
  - `pathfinding_costs`
  - `door_connections`
- Validation:
  - all lists default to empty rather than null
  - pathfinding costs only include currently relevant targets
  - room and zone mapping MUST agree when a tilemap is present

### PathSegment (ephemeral + persisted in snapshot payload)

- Purpose: represent server-computed movement waypoints for one movement action.
- Fields:
  - `waypoints: list[TilePosition]`
  - `path_cost`
  - `target_zone_id`
  - `target_object_id` (optional)
- Validation:
  - waypoints MUST be walkable tiles
  - first waypoint MUST align with current tile or next legal tile
  - final waypoint MUST reach the requested room or object target

### WorldSnapshot (ephemeral transport contract)

- Purpose: authoritative per-tick payload for live view and replay.
- Fields:
  - `schema_version`
  - `tick_number`
  - `sim_time`
  - `time_of_day`
  - `scenario_id`
  - `agents[]`
  - `conversations[]`
  - `world_events[]`
  - `camera_hints`
  - `selected_agent_id` (optional)
- Agent item fields:
  - `agent_id`, `name`, `zone_id`, `zone_name`
  - `position`
  - `target`
  - `path`
  - `mood`
  - `emoji`
  - `action`
  - `speech`
  - `thought`
  - `needs`
  - `goal`
  - `recent_decisions`
- Validation:
  - snapshot order MUST follow authoritative tick order
  - live and replay payloads MUST use the same schema version

### ConversationBubble (transport/UI contract)

- Purpose: describe speech or thought overlays shown over agents.
- Fields:
  - `agent_id`
  - `bubble_type` (`speech` | `thought`)
  - `content`
  - `tone`
  - `target_agent_id` (optional)
  - `expires_after_ms`
- Validation:
  - bubbles are optional and short-lived
  - absence of a bubble MUST not imply missing communication state

## Existing Entity Relationships

- `Scenario` MAY have zero or one `TileMapConfig`
- `AgentStateSnapshot` belongs to one `Agent` and MAY include one tile position
- `WorldSnapshot` is assembled from `AgentStateSnapshot`, `SimulationEvent`, `DecisionLog`,
  `Message`, and tilemap metadata but is not itself persisted as a table in the MVP
- `SpatialPerception` is derived from `TileMapConfig`, current agent positions, objects, and
  resources for one tick

## State Transitions

### Live tick state

1. load map metadata and collision grid
2. determine current tile position for each agent
3. compute `SpatialPerception`
4. resolve decision with spatial context
5. compute path if action is movement
6. update tile coordinates and zone membership
7. persist `AgentStateSnapshot`
8. assemble `WorldSnapshot`
9. broadcast `WorldSnapshot` to connected clients

### Replay state

1. request tick range
2. load stored snapshots or reconstruct replay payloads from persisted tick state
3. emit ordered `WorldSnapshot` array
4. client plays snapshots locally without changing backend truth

## Backward Compatibility Rules

- Zone-only scenarios remain valid with `TileMapConfig` absent.
- `tile_x` and `tile_y` remain nullable for all existing scenarios.
- Existing analytics and Streamlit pages continue to use persisted data without requiring
  tilemap awareness.
