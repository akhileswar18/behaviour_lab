# Tilemap Contract: Phase 5 2D Embodied Simulation World

## Format

- **Editor**: Tiled
- **Export Type**: JSON
- **Shared Asset Path**: `maps/house.json`
- **Client Copy Path**: `client/public/assets/maps/house.json`

## Required Map Metadata

- `tilewidth`: `16`
- `tileheight`: `16`
- `width`: grid width in tiles
- `height`: grid height in tiles
- `layers`: ordered array containing required visual, collision, and object layers

## Required Layers

### 1. `floor`

- Type: tile layer
- Purpose: base walkable floor rendering

### 2. `walls`

- Type: tile layer
- Purpose: walls and structural boundaries

### 3. `furniture`

- Type: tile layer
- Purpose: furniture and decorative props that may influence pathfinding or affordances

### 4. `collision`

- Type: tile layer or object layer
- Purpose: authoritative walkability mask for server-side pathfinding
- Contract:
  - non-empty collision tiles or flagged objects represent blocked cells
  - backend loader converts this into a boolean collision grid

### 5. `objects`

- Type: object layer
- Purpose: room definitions, affordances, door markers, and special interaction objects
- Contract:
  - room rectangles MUST have a `zone` custom property matching an existing `Zone.name`
  - affordance objects SHOULD include `affordance_type`
  - optional object properties MAY include `resource_type`, `interaction_radius`, `seat`,
    `bed`, `appliance`, or `door`

## Zone Mapping Rules

- Each room or area that should map to the existing zone system MUST be represented by a
  rectangle object in the `objects` layer.
- Each zone rectangle MUST have:
  - `name`
  - `zone`
- The `zone` property value MUST match an existing scenario zone identifier or name used by
  the backend scenario configuration.
- Multiple rectangles MAY map to the same logical zone if the scenario needs split areas.

## Backend Loader Responsibilities

The Python backend MUST load the map and derive:

- grid dimensions
- collision grid
- room boundary lookup
- zone-to-room mapping
- door connections
- object affordance registry

The backend MUST NOT depend on renderer-only fields for simulation correctness.

## Phaser Loader Responsibilities

The Phaser client MUST load the same JSON and use it to:

- render floor, walls, and furniture layers
- optionally visualize collision for debugging
- place agents at tile coordinates supplied by the backend
- align room labels, minimap, and overlays to authoritative map coordinates

The Phaser client MUST NOT redefine collision or room semantics differently from the backend.

## Compatibility Rules

- Map files MUST remain loadable by both backend and frontend without manual edits.
- Missing optional properties MAY degrade overlays or affordance detail, but missing required
  layers or `zone` mappings are contract violations.
- Zone-only scenarios MAY omit a tilemap entirely; embodied scenarios MUST supply a valid map
  contract.
