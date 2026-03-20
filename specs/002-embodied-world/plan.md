# Implementation Plan: Phase 5 2D Embodied Simulation World

**Branch**: `002-embodied-world` | **Date**: 2026-03-19 | **Spec**: `C:\Users\akhil\behaviour_lab\specs\002-embodied-world\spec.md`
**Input**: Add a Phaser 3 plus React embodied world viewer with backend spatial grounding,
FastAPI WebSocket broadcasts, and replay controls while keeping Python authoritative.

## Summary

Phase 5 adds a browser-based 2D embodied world to the existing Behavior Lab platform.
The new viewer is additive: the FastAPI + SQLite + Streamlit stack stays intact, while a
separate Phaser 3 + React client renders tile-based space, interpolated sprite movement,
conversation overlays, and replay controls from backend state.

Primary outcome: the backend understands tile-level space and broadcasts versioned
`WorldSnapshot` payloads over WebSocket, while the client renders those snapshots
without owning simulation logic.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/JavaScript (frontend)  
**Primary Dependencies**: Backend: FastAPI, SQLModel, Pydantic, pydantic-settings, pytest; Frontend: Phaser 3, React 18, Vite, TypeScript  
**Storage**: SQLite (existing) + Tiled JSON maps (static files)  
**Testing**: Backend: pytest (unit, integration, scenario, contract); Frontend: Vitest + Playwright (optional, stretch goal)  
**Target Platform**: Local desktop - Python backend + Vite dev server  
**Project Type**: Monorepo with Python backend + TypeScript frontend  
**Agent Scale Target**: 2-5 agents in a 5-room house  
**Time Model**: Tick-based (existing) + client-side interpolation for smooth rendering  
**Observability Surface**: Phaser 2D world + Streamlit dashboard + structured event logs  
**Real-Time Transport**: FastAPI WebSocket for tick snapshots, REST for tilemaps and replay ranges  
**Spatial World Format**: Tiled JSON tilemap shared by backend and frontend  
**Performance Goals**: <100ms WebSocket broadcast per tick, 60fps renderer, A* pathfinding <1ms for 40x30 grid  
**Constraints**: Server-authoritative, renderer is read-only, no sim logic in browser, backward compatible with zone scenarios  
**Scale/Scope**: Additive embodied world only; no vector memory, 3D, narrative director, or dashboard rewrites

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gate Review

- [x] I. Behavior-first scope: the renderer exists to expose and ground behavior, not to
      introduce entertainment-first logic.
- [x] II. Python-first simplicity: backend spatial logic uses lightweight in-repo parsing and
      pathfinding instead of heavy engine dependencies.
- [x] III. Modular architecture: cognition, world, transport, persistence, dashboard, and
      renderer remain distinct modules.
- [x] IV. Observable-by-design: movement, tile positions, path segments, overlays, and room
      transitions are emitted as structured traces and snapshots.
- [x] V. Memory and persona impact: spatial context enriches decisions without moving memory
      or persona logic into the client.
- [x] VI. Persona influence: persona and needs continue to shape spatial movement and
      interactions.
- [x] VII. Communication consequences: speech bubbles and arcs mirror backend communication
      events that still change state.
- [x] VIII. Dashboard-and-world validation: spatial features validate in the 2D viewer while
      cognition remains visible in structured traces and dashboard panels.
- [x] IX. Scenario-first validation: the house scenario is small, explicit, and reproducible.
- [x] X. State-over-time continuity: tile coordinates extend the existing tick-based state
      model.
- [x] XI. Structured schema discipline: tilemaps, spatial perception, replay payloads, and
      WebSocket messages are versioned contracts.
- [x] XII. Fast iteration with safety rails: the feature is sliced backend-first and keeps
      the renderer additive.
- [x] XIII. Local-first baseline: backend, map files, Vite client, and replay all run
      locally.
- [x] XIV. Experiment readiness: room layouts and affordances can vary across scenarios and
      reruns.
- [x] XV. Incremental complexity: live view lands before replay and visual polish.
- [x] XVI. AI-assisted code quality: contracts, module seams, and typed payloads reduce
      cross-stack drift.
- [x] XVII. Milestone continuity: Phases 1-4 behavior remains intact and observable.
- [x] XVIII. Embodied spatial grounding: tile-based space enriches decision context and maps
      zones to rooms.
- [x] XIX. Renderer is read-only: browser code does not own decisions, state mutation, or
      pathfinding.
- [x] XX. WebSocket-first communication: live tick state is pushed over FastAPI WebSocket and
      heavy payloads stay on REST.
- [x] Embodied spatial grounding: tile-based world enriches agent perception and decision
      context.
- [x] Renderer is read-only: no simulation logic, decisions, or state mutations in the
      browser client.
- [x] WebSocket-first communication: tick state is pushed via WebSocket and heavy data uses
      REST.
- [x] Dashboard-and-world validation: spatial features are testable in the 2D world viewer
      without altering the dashboard.

## Project Structure

### Documentation (this feature)

```text
specs/002-embodied-world/
├── spec.md
├── plan.md
├── tasks.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── websocket-schema.md
    └── tilemap-contract.md
```

### Source Code (repository root)

```text
# Backend (extend existing)
app/
├── agents/                    # existing - no changes
├── api/
│   ├── routes/
│   │   ├── world_ws.py        # NEW: WebSocket endpoint for simulation broadcast
│   │   └── world_rest.py      # NEW: REST endpoints for tilemap, replay, spatial queries
│   └── schemas/
│       └── world.py           # NEW: WorldSnapshot, TilePosition, SpatialContext schemas
├── simulation/
│   ├── tick_engine.py         # MODIFIED: add spatial context to DecisionContext, persist tile positions
│   ├── pathfinding.py         # NEW: A* pathfinding on tile collision grid
│   ├── spatial_context.py     # NEW: compute nearby agents, objects, room for perception
│   └── tilemap_loader.py      # NEW: load Tiled JSON, extract collision grid, zone-to-room mapping
├── persistence/
│   ├── models.py              # MODIFIED: add tile_x, tile_y to AgentStateSnapshot; add TileMapConfig
│   └── repositories/
│       └── spatial_repository.py  # NEW: spatial queries (agents in room, nearby agents)
├── schemas/
│   └── spatial.py             # NEW: TilePosition, SpatialPerception, PathResult
└── ws/
    └── broadcaster.py         # NEW: WebSocket connection manager + tick broadcast

# Frontend (NEW - separate directory)
client/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── index.html
├── public/
│   └── assets/
│       ├── tilesets/          # 16x16 pixel art spritesheets (LimeZu or free alternatives)
│       └── maps/
│           └── house.json     # Tiled JSON export - the map
├── src/
│   ├── main.tsx               # React entry point
│   ├── App.tsx                # Layout: Phaser canvas + React side panel + timeline
│   ├── game/
│   │   ├── PhaserGame.tsx     # Phaser-React bridge component
│   │   ├── scenes/
│   │   │   ├── WorldScene.ts  # Main scene: tilemap, agents, bubbles, overlays
│   │   │   └── Preloader.ts   # Asset loading scene
│   │   ├── sprites/
│   │   │   └── AgentSprite.ts # Agent sprite with animation, label, mood badge
│   │   ├── ui/
│   │   │   ├── SpeechBubble.ts
│   │   │   ├── ThoughtCloud.ts
│   │   │   └── InteractionArc.ts
│   │   └── systems/
│   │       ├── Interpolation.ts
│   │       └── DayNight.ts
│   ├── panels/
│   │   ├── AgentDetailPanel.tsx
│   │   ├── TimelineBar.tsx
│   │   └── TopBar.tsx
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   ├── useSimulationState.ts
│   │   └── useReplay.ts
│   └── types/
│       └── world.ts
└── tests/

# Shared map (accessible to both backend and frontend)
maps/
└── house.json

# Tests (extend existing)
tests/
├── unit/
│   ├── test_pathfinding.py
│   ├── test_spatial_context.py
│   └── test_tilemap_loader.py
├── integration/
│   ├── test_websocket_broadcast.py
│   └── test_spatial_tick_integration.py
├── scenario/
│   └── test_embodied_scenario.py
└── contract/
    ├── test_websocket_schema.py
    └── test_tilemap_contract.py
```

**Structure Decision**: Keep the Python backend inside `app/` and add a separate `client/`
Vite project plus shared `maps/` assets so backend and renderer can consume the same Tiled
JSON without sharing runtime state.

## Phase 0: Outline & Research

### Unknowns Extracted

- Unknown 1: How should the backend parse Tiled JSON without adding unnecessary dependencies?
- Unknown 2: What A* pathfinding implementation is sufficient for a small indoor grid?
- Unknown 3: How should the FastAPI WebSocket broadcaster fan out authoritative tick state
  to multiple clients safely?
- Unknown 4: How should zones map onto rooms and objects in the shared Tiled JSON map?
- Unknown 5: What interpolation strategy gives smooth client animation without violating
  backend authority?
- Unknown 6: How can tile coordinates extend `AgentStateSnapshot` without breaking zone-only
  scenarios?

### Research Tasks Dispatched

- Task: Evaluate lightweight Tiled JSON loading in Python that preserves shared map
  semantics.
- Task: Evaluate a minimal A* implementation for a 40x30 indoor collision grid.
- Task: Evaluate FastAPI native WebSocket connection-manager patterns for multi-client
  broadcasting.
- Task: Evaluate tilemap metadata conventions for room-to-zone mapping and affordance
  extraction.
- Task: Evaluate client-side interpolation strategies for snapshot-based sprite movement.
- Task: Evaluate backward-compatible persistence extensions for tile coordinates and map
  config.

### Consolidated Research Decisions

1. Use Python's built-in `json.load` plus a custom parser for Tiled JSON rather than adding a
   dedicated tilemap dependency.
2. Implement a lightweight pure-Python A* solver in `app/simulation/pathfinding.py`; the
   indoor grid is small enough that a custom implementation stays simple and fast.
3. Use FastAPI native `WebSocket` plus a connection manager list in `app/ws/broadcaster.py`
   for multi-client fan-out and graceful disconnect handling.
4. Use a Tiled object layer with rectangle objects carrying a `zone` custom property to map
   existing zones onto rooms or areas and additional object properties to expose affordances.
5. Use client-side linear interpolation between two authoritative tick snapshots; the client
   never predicts beyond the latest received state.
6. Extend `AgentStateSnapshot` with nullable `tile_x` and `tile_y` integer fields to preserve
   full backward compatibility for zone-only scenarios.

## Phase 1: Design & Contracts

### A. Backend Spatial Foundation

The backend loads a shared Tiled JSON map at startup, extracts:

- collision grid for pathfinding
- zone/room boundaries from object layers
- door and connection metadata
- object affordances (resource, seat, bed, appliance, etc.)

This state remains in memory for simulation use and is referenced by scenario bindings.

### B. Tile Position and Spatial Perception

`AgentStateSnapshot` gains nullable `tile_x` and `tile_y`. The tick engine computes:

- current room/zone from tile position
- nearby agents within a configurable radius
- nearby objects and affordances
- pathfinding cost to relevant resources or targets

That data becomes `SpatialPerception` and is injected into `DecisionContext` before the
deterministic or hybrid decision path runs.

### C. WebSocket and REST Transport

Transport responsibilities split cleanly:

- WebSocket `/ws/simulation`: live `tick_update`, connection handshake, client control
  commands, and selection events
- REST `/api/world/map`: tilemap and map metadata
- REST `/api/world/replay/{start}/{end}`: persisted historical snapshots or replay payloads
- REST `/api/world/agents/{agent_id}` or equivalent lightweight detail helpers MAY be added
  later if the side panel needs more than the per-tick snapshot

The backend stays authoritative and the simulation continues running if no clients are
connected.

### D. Frontend Renderer Architecture

The frontend is created from the official Phaser + React Vite template and split into:

- React layout shell for top bar, side panel, and timeline controls
- Phaser world scene for tilemap, sprites, labels, bubbles, overlays, and camera
- hooks for WebSocket state, live snapshot buffering, and replay mode
- typed contracts in `client/src/types/world.ts` matching the backend schema

The React layer never mutates simulation state directly. User actions are commands back to the
backend.

### E. Contracts

#### WebSocket message contract

Defined in `contracts/websocket-schema.md` with:

- message types: `connection_ack`, `tick_update`, `agent_selected`, `sim_control`,
  `replay_request`
- `schema_version: "1.0"`
- agent snapshot shape including position, path, mood, action, goal, conversation, and
  overlays

#### Tilemap contract

Defined in `contracts/tilemap-contract.md` with:

- required Tiled layers: `floor`, `walls`, `furniture`, `collision`, `objects`
- room-to-zone mapping through rectangle objects with `zone` property
- collision semantics, affordance properties, and shared backend/frontend interpretation rules

### F. End-to-End Data Flow

1. At startup, Python loads `maps/house.json`, derives collision grid, room boundaries, and
   zone mappings, and keeps them in memory.
2. At startup, the browser client loads the same Tiled JSON from its public assets and renders
   all visual layers in Phaser.
3. Each tick:
   - existing tick engine resolves goals and decisions
   - if action is movement, backend A* computes tile waypoints
   - backend updates `tile_x`, `tile_y` and zone/room membership
   - backend computes `SpatialPerception` and adds it to decision context
   - backend assembles a `WorldSnapshot`
   - backend broadcasts the snapshot to all WebSocket clients
   - backend persists tick result and state snapshots as before
4. Client receives `WorldSnapshot`:
   - stores previous and current authoritative snapshots
   - interpolates sprite positions between them at render time
   - updates speech bubbles, thought clouds, interaction arcs, labels, and side panel state
5. Replay mode requests a historical tick range through REST, then plays those stored
   snapshots locally at a selected speed.

### G. Slice-by-Slice Roadmap

1. Slice A: Backend spatial foundation
   - tilemap loader, collision grid, zone-room mapping, nullable tile coordinates
2. Slice B: WebSocket infrastructure
   - broadcaster, world snapshot assembly, live WebSocket endpoint, REST map/replay endpoints
3. Slice C: Frontend skeleton
   - Vite + React + Phaser client with static tilemap rendering
4. Slice D: Agent sprites on the map
   - live sprites, room transitions, click selection, basic movement animation
5. Slice E: Interpolation and visual overlays
   - lerp, labels, speech bubbles, thought clouds, interaction arcs
6. Slice F: Side panel and controls
   - top bar, selection panel, play/pause/speed, timeline scrubber
7. Slice G: Spatial perception for cognition
   - backend spatial context in `DecisionContext`, prompt builder, and deterministic policy
8. Slice H: Replay mode
   - REST replay endpoint, client playback state, camera follow
9. Slice I: Polish
   - day/night overlay, minimap, multi-client validation, performance checks, docs

### H. Risks, Tradeoffs, and What to Avoid

- Risk: renderer and backend drift apart.
  - Mitigation: one shared schema contract, backend authority, and contract tests.
- Risk: pathfinding or spatial context adds too much complexity to the current tick loop.
  - Mitigation: keep the map small, implement lightweight A*, and scope to indoor movement.
- Risk: replay payloads become too large for WebSocket.
  - Mitigation: keep replay on REST and reserve WebSocket for live ticks.
- Risk: zone-only scenarios break.
  - Mitigation: keep tile fields nullable and gate spatial behavior on map presence.

Avoid:

- putting simulation logic, decisions, or pathfinding into Phaser or React
- changing Streamlit pages as part of this feature
- introducing 3D, full physics, narrative director, or reflective memory scope
- requiring cloud services, auth, or external real-time infrastructure

### I. Acceptance Criteria

1. The browser client shows the shared tilemap and authoritative agent positions from live
   backend data.
2. The backend computes and persists tile coordinates without breaking zone-only scenarios.
3. At least one movement decision is influenced by `SpatialPerception` and traceable in logs
   and the renderer.
4. Replay mode renders correct historical world state for requested tick ranges.
5. Multiple clients can observe the same simulation without changing simulation behavior.

### Post-Design Constitution Re-Check

- [x] Embodied world enriches behavior rather than replacing it.
- [x] Backend remains authoritative for simulation, pathfinding, and persistence.
- [x] WebSocket and REST boundaries are explicit and versioned.
- [x] Existing dashboard and zone-only behavior remain intact.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Separate TypeScript frontend in `client/` | Phaser 3 plus React requires a browser codebase distinct from Python | Embedding renderer logic in Streamlit or Python would violate the renderer boundary and make 60fps animation impractical |
| WebSocket transport for live observation | Real-time embodied viewing requires low-latency snapshot pushes | Polling REST for every tick would add lag, duplicate state handling, and weaken multi-client behavior |
