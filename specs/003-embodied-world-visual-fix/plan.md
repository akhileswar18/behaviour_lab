# Implementation Plan: Embodied World Visual Quality Fix

**Branch**: `003-embodied-world-visual-fix` | **Date**: 2026-03-20 | **Spec**: `C:\Users\akhil\behaviour_lab\specs\003-embodied-world-visual-fix\spec.md`
**Input**: Feature specification from `/specs/003-embodied-world-visual-fix/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

This feature completes the visual side of the embodied world that Phase 5 introduced but
left in debug-placeholder form. The backend spatial model, tile coordinates, WebSocket
snapshot stream, and pathfinding stay authoritative and unchanged; the work lands entirely
in the `client/` renderer plus static pixel-art assets so the browser shows a believable
house, animated characters, readable overlays, smooth interpolation, and a useful agent
inspection panel.

## Technical Context

**Language/Version**: TypeScript/JavaScript (frontend), Python 3.11+ (backend unchanged)  
**Primary Dependencies**: Frontend: Phaser 3, React 18, Vite, TypeScript; Backend compatibility only: FastAPI, Pydantic, pytest  
**Storage**: Static Tiled JSON and PNG assets in `client/public/assets/`; existing SQLite and backend persistence remain unchanged  
**Testing**: Browser visual verification, existing backend pytest suites, optional Vitest coverage for interpolation and panel formatting logic  
**Target Platform**: Local desktop development with Python backend plus Vite dev server in any modern browser  
**Project Type**: Frontend visual-quality fix within an existing Python + React/Phaser monorepo  
**Agent Scale Target**: 2-5 agents in the existing embodied household scenario  
**Time Model**: Existing tick-based authoritative snapshots plus client-side frame interpolation between ticks  
**Observability Surface**: Phaser 2D world viewer, React side panel, minimap, and existing backend traces  
**Real-Time Transport**: Existing FastAPI WebSocket live snapshots plus existing REST map/replay endpoints  
**Spatial World Format**: Tiled JSON tilemap with external tileset PNGs and named object-layer zone rectangles  
**Performance Goals**: 60fps rendering, smooth lerp during live observation, no visible jank for 2-5 agents on a small house map  
**Constraints**: Client-only changes, no new npm packages, Streamlit dashboard untouched, renderer remains read-only, existing WebSocket/REST contracts preserved  
**Scale/Scope**: Improve visual quality of the existing embodied client only; no new simulation mechanics, no protocol changes, no persistence redesign

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gate Review

- [x] I. Behavior-first: the work makes existing embodied behavior visible rather than adding new simulation logic.
- [x] II. Python-first: no backend redesign or new Python dependency is required; the fix is frontend-scoped.
- [x] III. Modular: changes stay isolated to `client/` plus static assets, with backend compatibility preserved.
- [x] IV. Observable-by-design: the feature directly improves observability through better map rendering, overlays, and side-panel presentation.
- [x] V. Memory impact: memory behavior is unchanged; the renderer simply presents existing rationale and conversation output more clearly.
- [x] VI. Persona impact: persona differences become easier to observe through distinct agent visuals and readable recent decisions.
- [x] VII. Communication consequences: existing speech and thought events remain backend-authored and are rendered with better visual treatment.
- [x] VIII. Dashboard-and-world validation: the world viewer becomes practically usable for validation without changing the dashboard.
- [x] IX. Scenario-first: the plan validates against the existing 3-agent, 5-room seeded embodied scenario.
- [x] X. State-over-time continuity: interpolation makes tick-to-tick temporal progression visible without changing authoritative state.
- [x] XI. Structured data: the tilemap uses structured Tiled JSON and the renderer consumes existing typed world snapshots.
- [x] XII. Fast iteration: work is broken into visually testable slices that can be validated in the browser independently.
- [x] XIII. Local-first: Tiled, local assets, backend, and Vite all run on one machine with no cloud dependency.
- [x] XIV. Experiment-friendly: the renderer can swap house maps and sprite assets without changing the backend contract.
- [x] XV. Incremental: six user stories map cleanly to independent implementation slices in strict priority order.
- [x] XVI. Code quality: typed TypeScript, Phaser-native rendering, and contract documents keep the visual system maintainable.
- [x] XVII. Milestone success: this lands the missing "alive moment" by making agents visibly live in a house.
- [x] XVIII. Embodied spatial grounding: the house tilemap makes rooms, doors, furniture, and movement legible for the first time.
- [x] XIX. Renderer read-only: all state remains backend-authored; the client only interpolates and presents snapshots.
- [x] XX. WebSocket-first: the existing transport stays intact, with live updates on WebSocket and heavier payloads on REST.

## Project Structure

### Documentation (this feature)

```text
specs/003-embodied-world-visual-fix/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── tilemap-format-contract.md
│   └── sprite-asset-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
client/
├── public/
│   └── assets/
│       ├── tilesets/
│       │   ├── interiors.png
│       │   └── agents/
│       │       ├── agent_1.png
│       │       ├── agent_2.png
│       │       └── agent_3.png
│       ├── maps/
│       │   └── house.json
│       └── ATTRIBUTION.md
├── src/
│   ├── game/
│   │   ├── scenes/
│   │   │   ├── Preloader.ts
│   │   │   └── WorldScene.ts
│   │   ├── sprites/
│   │   │   └── AgentSprite.ts
│   │   ├── ui/
│   │   │   ├── SpeechBubble.ts
│   │   │   ├── ThoughtCloud.ts
│   │   │   └── InteractionArc.ts
│   │   └── systems/
│   │       ├── Interpolation.ts
│   │       └── DayNight.ts
│   └── panels/
│       └── AgentDetailPanel.tsx
└── tests/

maps/
└── house.json
```

**Structure Decision**: Keep the fix constrained to the existing `client/` application and
shared map assets. No new runtime modules or backend subsystems are introduced; the existing
frontend stubs in Phaser and React are upgraded from placeholder rendering to production-ready
visuals.

## Phase 0: Outline & Research

### Unknowns Extracted

- Unknown 1: Which free indoor tileset should back the house map, and how should it be exported for Phaser loading?
- Unknown 2: What Tiled layer structure and naming convention best support Phaser rendering and backend compatibility?
- Unknown 3: What spritesheet layout should character assets use so Phaser animations stay simple and repeatable?
- Unknown 4: What interpolation buffer and timing model best smooth existing authoritative snapshots?
- Unknown 5: What in-canvas speech and thought bubble approach gives readable overlays without adding dependencies?
- Unknown 6: What styling approach should the React side panel use so it fits the current dark theme without adding a CSS framework?

### Research Tasks Dispatched

- Task: Evaluate free 16x16 indoor pixel-art tilesets suitable for repository use and Phaser loading.
- Task: Evaluate Tiled JSON export conventions for Phaser `tilemapTiledJSON` plus backend zone extraction compatibility.
- Task: Evaluate Phaser-compatible character spritesheet formats for 4-direction movement and idle handling.
- Task: Evaluate snapshot interpolation patterns for renderer-only smoothing in an authoritative tick-based world.
- Task: Evaluate Phaser-native approaches for readable speech bubbles, thought clouds, and interaction arcs.
- Task: Evaluate the existing `AgentDetailPanel.tsx` structure and choose the lightest-weight styling path for a polished dark-theme panel.

### Consolidated Research Decisions

1. Use a single external indoor tileset atlas stored as `client/public/assets/tilesets/interiors.png` and keep the Tiled JSON referencing the PNG externally rather than embedding image data.
2. Standardize the house map on the layer set `floor`, `walls`, `furniture`, `furniture_upper`, `collision`, and `objects`, with object-layer rectangles carrying a `zone` property that matches backend zone names exactly.
3. Use per-agent 16x16 spritesheets with 4 columns by 4 rows where rows map to directions and columns map to animation frames; keep `agent_1`, `agent_2`, and `agent_3` texture keys stable.
4. Interpolate between a two-snapshot buffer in `WorldScene.update()` using elapsed real time since the last authoritative tick and clamp the lerp factor to avoid overshoot.
5. Build speech bubbles, thought clouds, and interaction arcs with Phaser-native graphics and text objects rather than DOM overlays or new UI libraries.
6. Keep the side panel inside React with existing project styling patterns, dark-theme CSS variables, and plain CSS/inline styles instead of Tailwind or new component packages.

## Phase 1: Design & Contracts

### A. Visual Renderer Scope

The backend spatial systems from `specs/002-embodied-world/` remain authoritative for tile
coordinates, pathfinding, world snapshots, and conversation data. This feature only upgrades
how the existing client loads map assets, renders the world, interpolates motion, and exposes
agent detail state so the same embodied data becomes immediately legible in the browser.

### B. Tilemap Design Specification

The renderer and shared map assets standardize on a single indoor house layout:

- Grid size: 40 tiles wide by 30 tiles tall.
- Native tile size: 16x16 pixels.
- Display assumption: Phaser renders at pixel-art scale and camera crops the larger house layout into the current viewport.
- Rooms:
  - Kitchen in the top-left.
  - Living Room in the top-right.
  - Bedroom in the bottom-left.
  - Bathroom in the bottom-right.
  - Commons hallway in the center corridor connecting all rooms.
- Walls:
  - 2-tile-thick exterior walls.
  - 1-tile-thick interior walls with 2-tile-wide door openings.
- Furniture:
  - Kitchen: stove, fridge, small table, 2 chairs.
  - Living Room: couch, coffee table, bookshelf, TV stand.
  - Bedroom: bed, wardrobe, nightstand.
  - Bathroom: toilet, sink, bathtub or shower.
  - Commons: coat rack, small rug, doormat.
- Tiled layers:
  - `floor`
  - `walls`
  - `furniture`
  - `furniture_upper`
  - `collision`
  - `objects`
- Zone objects:
  - Rectangle objects in `objects`.
  - Each includes a `zone` custom property.
  - Zone values must match scenario/backend room names exactly: `kitchen`, `bedroom`, `living_room`, `bathroom`, `commons`.

### C. Asset Loading Design

`Preloader.ts` changes from loading only `/api/world/map` to loading the real public assets:

- `house.json` from `client/public/assets/maps/house.json`
- `interiors.png` from `client/public/assets/tilesets/interiors.png`
- `agent_1.png`, `agent_2.png`, `agent_3.png` from `client/public/assets/tilesets/agents/`

The scene still preserves a fallback path:

- if the tilemap or tileset image fails, the world falls back to the existing rectangle layout with a console warning
- if an agent spritesheet is missing, the agent falls back to a colored marker with its initial and keeps selection enabled
- if a scenario is zone-only, the existing room-outline renderer stays available as a degraded but readable mode

### D. Tilemap Rendering Design

`WorldScene.ts` replaces programmatic room rectangles with Phaser tilemap rendering:

- create the map with `this.make.tilemap({ key: "world-map" })`
- add the tileset image through `map.addTilesetImage(...)`
- create visual layers in render order:
  1. `floor`
  2. `walls`
  3. `furniture`
  4. agent sprites
  5. `furniture_upper`
  6. overlays
- build collision from the `collision` tile layer so the visual map matches backend walkability
- keep camera follow, panning, and zoom behavior, then refine recenter and minimap behavior in the polish slice

### E. Sprite Animation Specification

Character presentation standardizes on a simple shared convention:

- one spritesheet per agent: `agent_1.png`, `agent_2.png`, `agent_3.png`
- frame size: 16x16 pixels
- layout: 4 columns by 4 rows
- row order:
  - row 0: down
  - row 1: left
  - row 2: right
  - row 3: up
- walk cycle: 4 frames per direction
- idle: first frame of the down-facing row
- scale: render at 3x so each character appears at 48x48 on screen
- animation keys:
  - `walk_down`
  - `walk_left`
  - `walk_right`
  - `walk_up`
  - `idle`
- animation frame rate: 8 fps
- identity mapping:
  - first known agent maps to `agent_1`
  - second to `agent_2`
  - third to `agent_3`
  - additional agents reuse a deterministic fallback mapping plus a readable marker fallback when art is unavailable

### F. Interpolation Fix Specification

The movement fix uses renderer-only smoothing and never predicts new simulation state:

- maintain `previousSnapshot` and `currentSnapshot`
- record `lastTickTimestamp` when a new authoritative snapshot arrives
- derive `estimatedTickInterval` from the last two arrival timestamps, with a fallback default of 2000ms
- every `WorldScene.update(time, delta)` frame:
  - compute `t = clamp((Date.now() - lastTickTimestamp) / estimatedTickInterval, 0, 1)`
  - interpolate each agent position between `previousSnapshot` and `currentSnapshot`
  - update sprite coordinates every frame, not just on WebSocket receipt
- direction detection:
  - compute `dx` and `dy` from previous tile to current tile
  - use the dominant axis to choose `walk_left`, `walk_right`, `walk_up`, or `walk_down`
  - switch to `idle` when `t >= 1` or when there is no movement delta
- guardrails:
  - clamp `t` to `[0, 1]`
  - snap to final position once `t >= 0.95` to avoid end-of-tick wobble

### G. Overlay and Panel Design

The existing debug overlays become readable production visuals:

- `SpeechBubble.ts`
  - Phaser-native rounded rectangle bubble
  - white or off-white fill with dark text
  - triangular tail pointing to the speaker
  - max 2-3 lines
  - truncate after roughly 60 characters
  - auto-fade after 4 seconds
- `ThoughtCloud.ts`
  - lighter cloud-style container visually distinct from speech
  - short rationale or thought text
  - smaller connector circles instead of a speech tail
- `InteractionArc.ts`
  - warm amber dashed or dotted line
  - subtle animation on active conversation
  - fade out when conversation ends
- `AgentDetailPanel.tsx`
  - dark-theme agent header with name, zone, and current state
  - colored needs bars using urgency thresholds
  - goal card with priority and target
  - scrollable decision log with the latest 10 entries
  - conversation transcript for recent messages involving the selected agent
  - styling implemented with existing React patterns and project-level CSS rather than a new framework

### H. Day/Night and Minimap Design

Final polish keeps the viewer readable while adding atmosphere:

- `DayNight.ts` maps `time_of_day` to a tint overlay:
  - noon around `0.5`: nearly clear
  - sunrise around `0.25`: soft gold
  - sunset around `0.75`: warm orange
  - midnight around `0.0` and `1.0`: deep blue
- minimap upgrades from black-box dots to a tiny representation of the real house layout or room outlines aligned to the tilemap
- camera behavior keeps follow mode, adds smoother recentering, and supports double-click reset to a centered overview

### I. Interface Contracts

This feature adds two explicit Phase 1 contracts:

- `contracts/tilemap-format-contract.md`
  - documents required Tiled JSON layers, tileset references, object properties, collision semantics, and fallback expectations
- `contracts/sprite-asset-contract.md`
  - documents spritesheet dimensions, row and column layout, naming, animation assumptions, and fallback rules

### J. End-to-End Visual Data Flow

1. `Preloader.ts` loads `house.json`, `interiors.png`, and the per-agent spritesheets.
2. `WorldScene.create()` builds the tilemap, creates the visible layers, and prepares agent visual containers.
3. The backend continues broadcasting authoritative `tick_update` snapshots over the existing WebSocket channel.
4. On every received snapshot:
   - `currentSnapshot` shifts to `previousSnapshot`
   - the new payload becomes `currentSnapshot`
   - tick timing metadata updates
5. On every render frame:
   - interpolation computes agent positions
   - `AgentSprite.ts` updates sprite position and directional animation
   - speech bubbles, thought clouds, and interaction arcs update
   - minimap and day/night overlay refresh
6. When an agent is selected:
   - the existing selection state updates
   - `AgentDetailPanel.tsx` re-renders with styled needs bars, goal card, decisions, and conversation transcript

### K. Slice-by-Slice Roadmap

1. Slice A: Asset acquisition and tilemap design
   - choose the tileset
   - place `interiors.png` and `agent_N.png` assets
   - build the 40x30 house in Tiled
   - export the real `house.json`
   - write `ATTRIBUTION.md`
2. Slice B: Tilemap rendering
   - update `Preloader.ts`
   - replace rectangle zones in `WorldScene.ts` with real tilemap layers
3. Slice C: Character sprites
   - update `AgentSprite.ts`
   - wire spritesheets and directional animations
   - preserve selection and fallback behavior
4. Slice D: Interpolation fix
   - implement two-snapshot buffering
   - render per-frame lerp
   - switch walk and idle animations from direction
5. Slice E: Speech, thought, and interaction overlays
   - replace debug text with styled bubbles and animated arcs
6. Slice F: Side-panel polish
   - upgrade `AgentDetailPanel.tsx` with needs bars, goal card, decision log, and transcript
7. Slice G: Day/night, minimap, and final polish
   - tune overlay colors
   - align minimap to the real house
   - refine camera reset and fallback handling

### L. Risks, Tradeoffs, and What to Avoid

- Risk: tileset licensing is unclear.
  - Mitigation: use only assets with explicit reuse terms and document every source in `client/public/assets/ATTRIBUTION.md`.
- Risk: the Tiled map does not match backend zone expectations.
  - Mitigation: require object-layer `zone` values to match `kitchen`, `bedroom`, `living_room`, `bathroom`, and `commons` exactly.
- Risk: spritesheet layout does not match Phaser animation assumptions.
  - Mitigation: keep a strict 16x16 4x4 contract and validate each sheet in isolation before final integration.
- Risk: interpolation introduces visible glitches at tick boundaries.
  - Mitigation: clamp lerp factor, keep a two-snapshot buffer, and snap to the final position near completion.

Avoid:

- modifying Python backend behavior beyond a minimal compatibility tweak if a real Tiled export requires it
- touching the Streamlit dashboard
- adding new WebSocket message types or changing existing backend contracts
- adding new npm dependencies for styling or rendering
- expanding the scope into outdoor maps, procedural generation, multiplayer, auth, 3D, or physics

### M. Acceptance Criteria

1. The browser shows a furnished pixel-art house with visible floors, walls, doors, and objects instead of rectangles.
2. Agents appear as animated pixel characters instead of colored circles whenever character assets are present.
3. Agents move smoothly between authoritative tile positions without teleporting.
4. Conversations and thoughts render as styled overlays instead of raw debug text.
5. The selected-agent panel shows colored needs bars, a goal card, a scrollable decision log, and recent conversation activity.
6. The existing backend embodied tests continue to pass without regressions to pathfinding, WebSocket broadcast, tile coordinates, or spatial context.
7. Third-party asset attribution is captured in `client/public/assets/ATTRIBUTION.md`.

### Post-Design Constitution Re-Check

- [x] Visual fixes make existing behavior observable; they do not add new simulation logic.
- [x] Backend authority and Python-first principles remain intact because the renderer stays read-only.
- [x] The plan preserves modular boundaries by limiting changes to `client/` and shared visual assets.
- [x] Tiled JSON remains the structured spatial source of truth for the renderer instead of ad-hoc drawing code.
- [x] Existing WebSocket and REST contracts remain valid and are only consumed more effectively by the client.
- [x] Each slice is independently verifiable in the browser with the seeded embodied scenario.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| External design-time tool (Tiled editor) | The house layout must be designed visually to ensure readable rooms, furniture placement, and door alignment | Hand-writing tile arrays in JSON is error-prone and cannot be validated visually before runtime |
| External pixel-art tileset and sprite assets | Phaser needs real image assets to replace the placeholder rectangles and circles | Programmatic drawing is the current broken experience and would not satisfy the visual-quality requirements |
