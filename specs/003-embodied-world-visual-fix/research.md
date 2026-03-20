# Research: Embodied World Visual Quality Fix

## Decision 1: Use an external 16x16 indoor tileset atlas with a stable Phaser path

**Decision**: Use a free 16x16 indoor pixel-art tileset exported as a single PNG atlas at
`client/public/assets/tilesets/interiors.png`, and keep the Tiled map referencing that PNG as
an external file rather than embedding image data in the JSON.

**Rationale**:

- Phaser tilemap loading is simplest when the JSON names a tileset image that can be loaded
  separately and matched with `map.addTilesetImage(...)`.
- External PNG references keep `house.json` readable, diffable, and easy to replace during
  iteration.
- A single indoor atlas covers floors, walls, and furniture in one consistent visual style,
  which reduces asset drift across layers.
- The feature needs repository-friendly asset attribution, so a stable file layout supports a
  clear `ATTRIBUTION.md`.

**Alternatives considered**:

- Embedded tileset image data inside the Tiled JSON: rejected because it makes the map file
  heavy and harder to inspect, diff, and maintain.
- Multiple small tileset atlases: rejected for the initial fix because it complicates loading
  and tile indexing without adding user-facing value.
- Continuing with programmatic rectangles: rejected because placeholder geometry is the
  specific problem this feature is meant to remove.

## Decision 2: Standardize the Tiled map on named layers plus exact zone rectangles

**Decision**: Design the house map in Tiled with layers named `floor`, `walls`, `furniture`,
`furniture_upper`, `collision`, and `objects`, and use rectangle objects in `objects` with a
required `zone` custom property matching backend zone names exactly: `kitchen`, `bedroom`,
`living_room`, `bathroom`, and `commons`.

**Rationale**:

- Phaser `this.make.tilemap()` plus `createLayer()` works cleanly when layer names are stable
  and explicit.
- The backend tilemap loader already expects structured layers and object-based zone metadata,
  so keeping those conventions avoids protocol drift.
- Separating `furniture_upper` from `furniture` allows tall objects to draw above sprites
  without changing simulation logic.
- A dedicated `collision` tile layer keeps walkability visible and structurally aligned with
  both renderer and backend expectations.

**Alternatives considered**:

- Encoding collision exclusively as tile properties on visual layers: rejected because a
  dedicated collision layer is easier to inspect and keeps visual art concerns separate from
  walkability.
- Using only room-name strings in code instead of Tiled objects: rejected because it would
  move spatial structure back into renderer logic.
- Keeping the current stub map shape and zone names: rejected because the new furnished house
  needs a richer layout and the contract must match the final room set.

## Decision 3: Use per-agent 16x16 4x4 spritesheets with deterministic texture keys

**Decision**: Character assets use one PNG per agent with 16x16 frames arranged as 4 columns
by 4 rows. Rows map to directions in the order down, left, right, up, and columns map to the
4-frame walk cycle. Texture keys remain `agent_1`, `agent_2`, and `agent_3`.

**Rationale**:

- Phaser `load.spritesheet()` and `anims.create()` work best with fixed-width sprite sheets and
  a consistent row/column convention.
- A per-agent file keeps identity mapping simple and supports visually distinct characters
  without a more complex atlas manifest.
- Reusing the first down-facing frame as idle keeps the animation set minimal while preserving
  direction-aware movement.
- The project only targets 2-5 agents, so per-agent spritesheets are easier to manage than a
  more abstract skinning system.

**Alternatives considered**:

- One giant shared character sheet with metadata: rejected for this scope because it adds
  mapping complexity the feature does not need.
- Directionless idle-only sprites: rejected because they would not solve the motion legibility
  problem.
- Continuing with circles and labels only: rejected because they do not satisfy the visual
  distinctness requirements.

## Decision 4: Interpolate with a two-snapshot buffer in the Phaser update loop

**Decision**: Store `previousSnapshot` and `currentSnapshot`, compute an estimated tick
interval from recent arrivals, and let `WorldScene.update()` interpolate every frame using
`t = clamp((Date.now() - lastTickTimestamp) / estimatedTickInterval, 0, 1)` with a 2000ms
fallback interval.

**Rationale**:

- The current bug is caused by always passing `1` to interpolation, which snaps instantly to
  the final position.
- A two-snapshot buffer is enough because the renderer is not predicting future state; it is
  only smoothing between authoritative positions.
- Using the render loop keeps motion smooth even when no new snapshot arrives during a frame.
- Deriving the interval from actual arrivals keeps animation aligned to real tick cadence while
  still falling back safely during startup or sparse updates.

**Alternatives considered**:

- Tweening directly on snapshot receipt: rejected because it is harder to coordinate across
  consecutive updates and can drift from authoritative timing.
- Predictive client movement: rejected because it would violate the renderer read-only
  boundary.
- Leaving interpolation disabled: rejected because teleporting movement breaks the embodied
  experience.

## Decision 5: Build speech and thought overlays with Phaser-native graphics

**Decision**: Implement speech bubbles, thought clouds, and interaction arcs using Phaser
graphics plus text objects instead of DOM overlays or extra UI libraries.

**Rationale**:

- Phaser-native overlays stay in world coordinates naturally, which keeps them aligned with
  camera movement, zoom, and follow mode.
- The existing overlay classes already live inside the Phaser scene, so upgrading them keeps
  the architecture simple.
- Rounded rectangles, connector tails, dashed arcs, alpha fades, and wrapped text can all be
  built with Phaser primitives without adding dependencies.
- Avoiding DOM overlays prevents layering and scaling issues over a moving canvas.

**Alternatives considered**:

- DOM-based floating overlays: rejected because they complicate coordinate syncing and camera
  transforms.
- Nine-slice plugin dependencies: rejected because the feature should not add new packages for
  a solvable canvas problem.
- Keeping raw debug text: rejected because it is the core usability defect this feature fixes.

## Decision 6: Keep the side panel in React with existing dark-theme styling patterns

**Decision**: Upgrade `AgentDetailPanel.tsx` using the current React structure, dark-theme CSS
variables, and lightweight component styling rather than introducing Tailwind, CSS modules, or
third-party UI kits.

**Rationale**:

- The feature is a visual-quality fix, not a UI framework migration.
- The current panel already exists in React and only needs better information hierarchy,
  progress bars, cards, and scrollable sections.
- Reusing existing styling patterns avoids dependency churn and keeps the scope centered on the
  embodied viewer.
- Needs bars, goal cards, and decision logs can be built with standard React markup and CSS.

**Alternatives considered**:

- Adding Tailwind or a component library: rejected because the repo does not need a styling
  stack change for one panel.
- Moving the panel into Phaser UI: rejected because the panel is better suited to React state
  and DOM scrolling.
- Leaving the plain text panel in place: rejected because it fails the inspection usability
  goals for researchers.
