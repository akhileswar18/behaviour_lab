# Data Model: Embodied World Visual Quality Fix

## Overview

This feature does not introduce new simulation entities. It defines the frontend-facing visual
entities, asset contracts, and renderer state needed to present the existing embodied world as
a readable pixel-art environment.

## Entity: WorldVisualAsset

**Purpose**: Represents the shared Tiled house map and its associated tileset image used by
both the backend-compatible map loader and the Phaser renderer.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mapKey` | string | Yes | Phaser cache key for the Tiled JSON map, fixed to `world-map`. |
| `mapPath` | string | Yes | Public asset path for `house.json`. |
| `tilesetKey` | string | Yes | Phaser cache key for the indoor tileset image. |
| `tilesetImagePath` | string | Yes | Public asset path for `interiors.png`. |
| `tileWidth` | integer | Yes | Native tile width in pixels; expected to be 16. |
| `tileHeight` | integer | Yes | Native tile height in pixels; expected to be 16. |
| `mapWidth` | integer | Yes | Tile columns in the house map; expected to be 40. |
| `mapHeight` | integer | Yes | Tile rows in the house map; expected to be 30. |
| `layerNames` | string[] | Yes | Ordered layer set the renderer expects. |
| `fallbackEnabled` | boolean | Yes | Whether the debug-safe rectangle fallback can be used if asset loading fails. |

**Validation rules**:

- `tileWidth` and `tileHeight` should be positive integers and are expected to be 16 for the primary art path.
- `layerNames` must include `floor`, `walls`, `furniture`, `furniture_upper`, `collision`, and `objects`.
- `mapWidth` and `mapHeight` must be large enough to contain the defined 5-room house layout.

**Relationships**:

- One `WorldVisualAsset` includes one or more `TileLayerVisual` records.
- One `WorldVisualAsset` includes one or more `ZoneDefinition` records.

## Entity: TileLayerVisual

**Purpose**: Describes one renderable or semantic layer inside the Tiled map.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Exact Tiled layer name. |
| `kind` | enum | Yes | One of `visual`, `collision`, `objects`. |
| `visible` | boolean | Yes | Whether the layer should render in the normal world view. |
| `renderOrder` | integer | No | Order relative to other visible layers. |
| `collidable` | boolean | Yes | Whether non-empty tiles are treated as blocked space. |

**Validation rules**:

- `name` must be unique within a map.
- `collision` must have `kind = collision` and `collidable = true`.
- `objects` must have `kind = objects`.

## Entity: ZoneDefinition

**Purpose**: Maps a named semantic room area onto a rectangle in the Tiled object layer.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `zone` | string | Yes | Backend-compatible zone identifier. |
| `x` | number | Yes | Rectangle origin in map coordinates. |
| `y` | number | Yes | Rectangle origin in map coordinates. |
| `width` | number | Yes | Rectangle width. |
| `height` | number | Yes | Rectangle height. |

**Validation rules**:

- `zone` must be one of `kitchen`, `bedroom`, `living_room`, `bathroom`, or `commons`.
- Zone rectangles should not be empty.
- Zone rectangles should align to the intended furnished room footprint and door layout.

## Entity: AgentVisualProfile

**Purpose**: Defines the visual asset and animation mapping used to represent one agent.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `textureKey` | string | Yes | Phaser texture key such as `agent_1`. |
| `assetPath` | string | Yes | Public PNG path for the spritesheet. |
| `frameWidth` | integer | Yes | Width of each frame in pixels; expected 16. |
| `frameHeight` | integer | Yes | Height of each frame in pixels; expected 16. |
| `walkRows` | object | Yes | Direction-to-row mapping for animation extraction. |
| `idleFrame` | integer | Yes | Default idle frame index. |
| `scale` | number | Yes | Render scale; expected 3. |
| `fallbackLabel` | string | Yes | Initial or short label shown if the spritesheet is unavailable. |

**Validation rules**:

- `frameWidth` and `frameHeight` must be positive and expected to match 16x16 assets.
- `walkRows` must define `down`, `left`, `right`, and `up`.
- `scale` must preserve readability without blurring pixel art.

## Entity: AgentRenderState

**Purpose**: Holds the per-agent visual state derived from authoritative snapshots and local
interpolation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agentId` | string | Yes | Stable agent identifier from the world snapshot. |
| `displayName` | string | Yes | Human-readable name shown in labels and the side panel. |
| `previousTile` | object | No | Previous authoritative tile position. |
| `currentTile` | object | Yes | Latest authoritative tile position. |
| `interpolatedPosition` | object | Yes | Current render-time pixel position. |
| `direction` | enum | Yes | `up`, `down`, `left`, `right`, or `idle`. |
| `animationState` | enum | Yes | `walking`, `idle`, or `fallback`. |
| `selected` | boolean | Yes | Whether the agent is selected in the UI. |
| `zone` | string | No | Current room or zone label for the panel and badge. |

**Validation rules**:

- `currentTile` must always come from the latest authoritative snapshot.
- `interpolatedPosition` must clamp to the current tile when interpolation completes.
- `direction` should reflect the dominant axis of movement between authoritative positions.

**State transitions**:

- `idle -> walking` when successive snapshots show a tile change.
- `walking -> idle` when interpolation reaches the latest authoritative tile or the agent stops moving.
- `walking -> fallback` if the sprite asset fails and the renderer swaps to a marker representation.

## Entity: OverlayBubble

**Purpose**: Represents a temporary speech or thought element drawn above an agent.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `overlayId` | string | Yes | Stable UI identifier for lifecycle management. |
| `agentId` | string | Yes | Speaker or thinker agent identifier. |
| `kind` | enum | Yes | `speech` or `thought`. |
| `rawText` | string | Yes | Original content from the authoritative snapshot. |
| `displayText` | string | Yes | Trimmed, wrapped, user-facing content. |
| `maxChars` | integer | Yes | Truncation boundary, expected around 60 characters. |
| `createdAtTick` | integer | Yes | Tick when the overlay appeared. |
| `expiresAfterMs` | integer | Yes | Fade-out duration, expected around 4000ms. |

**Validation rules**:

- `displayText` must never exceed the configured visual bounds without truncation or wrapping.
- `kind = speech` and `kind = thought` must remain visually distinct.
- Expired overlays must fade cleanly rather than persisting indefinitely.

## Entity: InteractionArcState

**Purpose**: Represents a visible conversational link between two agents.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sourceAgentId` | string | Yes | Conversation initiator or active speaker. |
| `targetAgentId` | string | Yes | Conversation counterpart. |
| `active` | boolean | Yes | Whether the arc should currently render. |
| `style` | enum | Yes | Expected to be `dashed-amber` for this feature. |
| `fadesOnEnd` | boolean | Yes | Whether the arc animates out after the interaction ends. |

## Entity: AgentDetailPanelView

**Purpose**: Normalized presentation model for the selected-agent side panel.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agentId` | string | Yes | Selected agent identifier. |
| `name` | string | Yes | Agent display name. |
| `zone` | string | No | Current room or zone. |
| `needs` | array | Yes | Needs summary with label, value, and urgency color. |
| `activeGoal` | object | No | Current goal type, target, and priority. |
| `decisionLog` | array | Yes | Most recent 10 decisions, latest first. |
| `conversationFeed` | array | Yes | Recent conversation entries involving the selected agent. |
| `moodLabel` | string | No | Lightweight mood or status indicator for the header. |

**Validation rules**:

- `needs` must include Hunger, Safety, and Social in a stable order.
- `decisionLog` should cap at 10 entries to keep the panel scannable.
- `conversationFeed` should prefer concise readable text over raw debug formatting.

## Entity: FallbackVisualMode

**Purpose**: Captures the renderer's degraded state when required assets cannot be loaded.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `worldFallback` | boolean | Yes | Whether room rectangles are replacing the full tilemap. |
| `agentFallback` | boolean | Yes | Whether one or more agents use marker visuals instead of sprites. |
| `warningMessage` | string | Yes | Console or diagnostic message explaining the degraded mode. |

**Validation rules**:

- Fallback mode must remain readable and selectable.
- The viewer must continue rendering rather than failing closed when assets are missing.

## Relationships Summary

- One `WorldVisualAsset` contains many `TileLayerVisual` layers and many `ZoneDefinition` areas.
- One `AgentVisualProfile` can be assigned to one or more `AgentRenderState` instances through deterministic identity mapping.
- One `AgentRenderState` can own many transient `OverlayBubble` records and participate in many `InteractionArcState` records.
- One selected `AgentRenderState` produces one `AgentDetailPanelView`.

## State Flow Summary

1. Assets load into `WorldVisualAsset` and `AgentVisualProfile`.
2. Live snapshots update `AgentRenderState` and overlay entities.
3. Per-frame interpolation advances `AgentRenderState.interpolatedPosition`.
4. Selection derives `AgentDetailPanelView`.
5. Missing assets toggle `FallbackVisualMode` without changing authoritative simulation state.
