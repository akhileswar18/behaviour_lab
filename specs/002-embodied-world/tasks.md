# Tasks: Phase 5 2D Embodied Simulation World

**Input**: Design documents from `/specs/002-embodied-world/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for story structure), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required for this phase. Execute backend unit, integration, scenario, contract, and
smoke coverage, with optional frontend Vitest coverage for hooks and interpolation helpers.

**Organization**: Tasks are grouped by user story and the requested delivery slices. Scope is
limited to embodied spatial grounding, read-only rendering, WebSocket transport, replay, and
associated contracts/docs.

## Format: `[ID] [P?] [Story?] Description with file path`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold the backend spatial modules, shared map assets, and separate frontend
codebase before core embodied behavior changes.

- [X] T001 Create Phase 5 feature spec artifacts in `specs/002-embodied-world/` and `specs/002-embodied-world/contracts/` [Deps: none] [Output: tracked spec, plan, tasks, research, data model, quickstart, and contracts for embodied world]
- [X] T002 Create `client/` Vite + React + Phaser 3 project scaffold in `client/package.json`, `client/vite.config.ts`, `client/tsconfig.json`, `client/index.html`, and `client/src/main.tsx` [Deps: none] [Output: standalone frontend module bootstrapped from the Phaser React template]
- [X] T003 [P] Create shared map directories `maps/`, `client/public/assets/maps/`, and `client/public/assets/tilesets/` with placeholder `.gitkeep` files and initial `maps/house.json` stub [Deps: none] [Output: shared map/asset layout available to backend and frontend]
- [X] T004 [P] Create backend scaffolds in `app/ws/broadcaster.py`, `app/simulation/pathfinding.py`, `app/simulation/spatial_context.py`, `app/simulation/tilemap_loader.py`, `app/api/routes/world_ws.py`, `app/api/routes/world_rest.py`, `app/schemas/spatial.py`, and `app/api/schemas/world.py` [Deps: none] [Output: backend embodied-world module stubs with importable placeholders]
- [X] T005 [P] Create frontend scene/system/panel stubs in `client/src/App.tsx`, `client/src/game/PhaserGame.tsx`, `client/src/game/scenes/WorldScene.ts`, `client/src/game/scenes/Preloader.ts`, `client/src/game/sprites/AgentSprite.ts`, `client/src/game/ui/SpeechBubble.ts`, `client/src/game/ui/ThoughtCloud.ts`, `client/src/game/ui/InteractionArc.ts`, `client/src/game/systems/Interpolation.ts`, `client/src/game/systems/DayNight.ts`, `client/src/panels/AgentDetailPanel.tsx`, `client/src/panels/TimelineBar.tsx`, `client/src/panels/TopBar.tsx`, `client/src/hooks/useWebSocket.ts`, `client/src/hooks/useSimulationState.ts`, `client/src/hooks/useReplay.ts`, and `client/src/types/world.ts` [Deps: T002] [Output: frontend files exist with typed module boundaries]

---

## Phase 2: Foundational (Backend Spatial + WebSocket)

**Purpose**: Build the spatial contracts, persistence extensions, and transport layer that
all user stories depend on.

**CRITICAL**: No user story implementation should complete until this phase is done.

- [X] T006 [P] Add unit tests for tilemap parsing in `tests/unit/test_tilemap_loader.py` [Deps: T004] [Output: failing tests for required Tiled JSON layers, zone mapping, and collision extraction]
- [X] T007 [P] Add unit tests for A* pathfinding in `tests/unit/test_pathfinding.py` [Deps: T004] [Output: failing tests for valid path generation, blocked tiles, and short-grid performance]
- [X] T008 [P] Add unit tests for spatial perception in `tests/unit/test_spatial_context.py` [Deps: T004] [Output: failing tests for nearby agents, room detection, and object affordances]
- [X] T009 [P] Add contract tests for the WebSocket schema in `tests/contract/test_websocket_schema.py` [Deps: T004] [Output: locked message-type and payload-shape expectations for `connection_ack`, `tick_update`, `sim_control`, `agent_selected`, and `replay_request`]
- [X] T010 [P] Add contract tests for the tilemap format in `tests/contract/test_tilemap_contract.py` [Deps: T003, T004] [Output: locked expectations for required layers, `zone` properties, and shared backend/frontend compatibility]
- [X] T011 [P] Add integration tests for WebSocket broadcast fan-out in `tests/integration/test_websocket_broadcast.py` [Deps: T004, T009] [Output: failing tests for multi-client connect, broadcast, and disconnect behavior]
- [X] T012 [P] Add integration tests for embodied tick-state persistence in `tests/integration/test_spatial_tick_integration.py` [Deps: T004, T006, T007, T008] [Output: failing tests for tile coordinate persistence and zone compatibility]
- [X] T013 Implement Tiled JSON loading in `app/simulation/tilemap_loader.py` [Deps: T006, T010] [Output: loader that parses layers, collision grid, zone rectangles, and object affordances from `maps/house.json`]
- [X] T014 Implement A* pathfinding in `app/simulation/pathfinding.py` [Deps: T007, T013] [Output: lightweight backend pathfinding on the collision grid]
- [X] T015 Extend persistence models in `app/persistence/models.py` with nullable `tile_x`, `tile_y`, and new `TileMapConfig` support [Deps: T012] [Output: backward-compatible SQLModel extensions for embodied scenarios]
- [X] T016 Update database initialization compatibility in `app/persistence/init_db.py` for embodied-world fields and config [Deps: T015] [Output: local SQLite schema supports tile coordinates and map bindings]
- [X] T017 Add spatial repository helpers in `app/persistence/repositories/spatial_repository.py` [Deps: T015] [Output: query layer for agents in room, nearby agents, and map config lookup]
- [X] T018 Define shared spatial schemas in `app/schemas/spatial.py` and `app/api/schemas/world.py` [Deps: T009, T015] [Output: typed `TilePosition`, `SpatialPerception`, `PathResult`, `WorldSnapshot`, and overlay payloads]
- [X] T019 Implement WebSocket connection manager and broadcaster in `app/ws/broadcaster.py` [Deps: T011, T018] [Output: multi-client broadcast manager with graceful connect/disconnect]
- [X] T020 Implement embodied-world REST endpoints in `app/api/routes/world_rest.py` [Deps: T013, T017, T018] [Output: `/api/world/map` and `/api/world/replay/{start}/{end}` endpoint handlers]
- [X] T021 Implement live simulation WebSocket endpoint in `app/api/routes/world_ws.py` [Deps: T019, T020] [Output: `/ws/simulation` endpoint with handshake and client message handling]
- [X] T022 Register embodied-world routes in `app/api/main.py` and `app/api/routes/__init__.py` as needed [Deps: T020, T021] [Output: backend serves embodied-world REST and WebSocket routes]

**Checkpoint**: Spatial contracts, transport, and persistence are ready; user story
implementation can proceed safely.

---

## Phase 3: User Story 1 - Watch Agents Live (Priority: P1)

**Goal**: Researchers can open the browser client, see the house map, watch live agent
movement, and inspect one selected agent.

**Independent Test**: Run a three-agent, five-room scenario for ten ticks and verify the
client shows the map, live sprites, labels, movement, and selected-agent detail panel.

### Tests for User Story 1

- [X] T023 [P] [US1] Add scenario test for live embodied observation in `tests/scenario/test_embodied_scenario.py` [Deps: T012, T021] [Output: failing scenario test asserting positions, room transitions, and broadcasts across ten ticks]
- [X] T024 [P] [US1] Add backend/frontend contract test for world snapshot typing in `tests/contract/test_websocket_schema.py` and `client/src/types/world.ts` [Deps: T009, T018] [Output: locked world snapshot fields shared across Python and TypeScript]
- [X] T025 [P] [US1] Add frontend hook/unit tests in `client/tests/useWebSocket.test.ts` and `client/tests/useSimulationState.test.ts` [Deps: T002, T005] [Output: failing frontend tests for message parsing and client state updates]

### Implementation for User Story 1

- [X] T026 [US1] Implement `WorldSnapshot` assembly from tick state in `app/api/schemas/world.py`, `app/ws/broadcaster.py`, and `app/simulation/tick_engine.py` [Deps: T018, T019, T023] [Output: authoritative per-tick payload built from persisted state and events]
- [X] T027 [US1] Extend `app/simulation/tick_engine.py` and `app/simulation/runner.py` to maintain tile positions and broadcast snapshots after each tick [Deps: T014, T017, T026] [Output: live embodied-state updates tied to the existing tick loop]
- [X] T028 [US1] Implement frontend application shell in `client/src/App.tsx`, `client/src/panels/TopBar.tsx`, and `client/src/game/PhaserGame.tsx` [Deps: T005] [Output: React layout with top bar, Phaser canvas container, and side panel slots]
- [X] T029 [US1] Implement asset preloading and world scene boot in `client/src/game/scenes/Preloader.ts` and `client/src/game/scenes/WorldScene.ts` [Deps: T003, T028] [Output: Phaser loads the shared tilemap and tilesets and starts the main scene]
- [X] T030 [US1] Implement live WebSocket and simulation-state hooks in `client/src/hooks/useWebSocket.ts` and `client/src/hooks/useSimulationState.ts` [Deps: T025, T028] [Output: client connects, reconnects, parses tick snapshots, and exposes state to React and Phaser]
- [X] T031 [US1] Implement `AgentSprite` rendering and selection in `client/src/game/sprites/AgentSprite.ts` and `client/src/game/scenes/WorldScene.ts` [Deps: T029, T030] [Output: authoritative sprites with labels, mood badge, and click-to-select bridge]
- [X] T032 [US1] Implement interpolation system in `client/src/game/systems/Interpolation.ts` and integrate it into `client/src/game/scenes/WorldScene.ts` [Deps: T030, T031] [Output: lerped movement between authoritative tick snapshots]
- [X] T033 [US1] Implement overlays in `client/src/game/ui/SpeechBubble.ts`, `client/src/game/ui/ThoughtCloud.ts`, and `client/src/game/ui/InteractionArc.ts` [Deps: T026, T031] [Output: conversation, thought, and interaction indicators derived from snapshot data]
- [X] T034 [US1] Implement selected-agent detail panel in `client/src/panels/AgentDetailPanel.tsx` [Deps: T030, T031] [Output: side panel with needs, goal, recent decisions, and conversation details]

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Spatial Grounding for Agent Cognition (Priority: P2)

**Goal**: Tile-level spatial perception meaningfully changes backend decision-making while
remaining visible in live observation.

**Independent Test**: Run a hungry-agent scenario and verify that the decision context uses
room, proximity, and pathfinding cost to choose a kitchen path.

### Tests for User Story 2

- [X] T035 [P] [US2] Add scenario test for spatially influenced behavior in `tests/scenario/test_embodied_scenario.py` [Deps: T023, T014] [Output: failing scenario assertion that at least one decision changes because of spatial context]
- [X] T036 [P] [US2] Add unit tests for `SpatialPerception` integration in `tests/unit/test_spatial_context.py` [Deps: T008, T018] [Output: failing tests for room membership, nearby agents, and pathfinding cost composition]
- [X] T037 [P] [US2] Add integration test for spatial decision context flow in `tests/integration/test_spatial_tick_integration.py` [Deps: T012, T018] [Output: failing integration test asserting `DecisionContext` receives spatial inputs]

### Implementation for User Story 2

- [X] T038 [US2] Implement room, proximity, and affordance queries in `app/simulation/spatial_context.py` and `app/persistence/repositories/spatial_repository.py` [Deps: T017, T036] [Output: backend `SpatialPerception` builder for current tick]
- [X] T039 [US2] Extend decision schemas and context in `app/schemas/decision_engine.py`, `app/schemas/spatial.py`, and `app/api/schemas/world.py` [Deps: T018, T037] [Output: `DecisionContext` and snapshot payloads carry spatial perception fields]
- [X] T040 [US2] Update `app/agents/prompt_builder.py` to include bounded spatial context for hybrid/LLM decisions [Deps: T039] [Output: prompt context contains room, nearby agents/objects, and path costs]
- [X] T041 [US2] Update `app/agents/decision_policy.py` and `app/agents/planning_policy.py` to consider spatial proximity and path cost in action selection [Deps: T038, T039] [Output: deterministic policy respects embodied world context]
- [X] T042 [US2] Update `app/simulation/tick_engine.py` to compute spatial perception before decision resolution and to persist authoritative path/position state [Deps: T038, T041] [Output: embodied cognition integrated into the existing tick loop]

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Replay and Observation Controls (Priority: P3)

**Goal**: Researchers can pause, replay, scrub, and follow agents through historical world
state without affecting live simulation truth.

**Independent Test**: Request a replay range, play it back at multiple speeds, and verify
camera follow plus historical side-panel state.

### Tests for User Story 3

- [X] T043 [P] [US3] Add integration test for replay range serving in `tests/integration/test_websocket_broadcast.py` and `tests/integration/test_spatial_tick_integration.py` [Deps: T020] [Output: failing tests for correct historical range retrieval and ordering]
- [X] T044 [P] [US3] Add frontend replay/control tests in `client/tests/useReplay.test.ts` and `client/tests/timeline.test.ts` [Deps: T005] [Output: failing frontend tests for replay state, speed changes, and scrub behavior]
- [X] T045 [P] [US3] Add scenario test for replay fidelity in `tests/scenario/test_embodied_scenario.py` [Deps: T023, T043] [Output: failing scenario assertion that replay world state matches stored ticks]

### Implementation for User Story 3

- [X] T046 [US3] Implement replay REST payload generation in `app/api/routes/world_rest.py` and `app/persistence/repositories/run_repository.py` or supporting query helpers [Deps: T043] [Output: replay endpoint returns ordered historical world snapshots]
- [X] T047 [US3] Implement replay hook and state management in `client/src/hooks/useReplay.ts` [Deps: T044, T046] [Output: client can load, play, pause, and scrub historical snapshots]
- [X] T048 [US3] Implement timeline controls in `client/src/panels/TimelineBar.tsx` and integrate them in `client/src/App.tsx` [Deps: T047] [Output: play/pause/speed/scrub UI controlling live vs replay mode]
- [X] T049 [US3] Implement replay rendering mode and camera follow in `client/src/game/scenes/WorldScene.ts` [Deps: T047, T048] [Output: Phaser scene can switch between live snapshots and replay snapshots and follow a selected agent]
- [X] T050 [US3] Implement day/night overlay and minimap in `client/src/game/systems/DayNight.ts` and `client/src/game/scenes/WorldScene.ts` [Deps: T049] [Output: visual observation polish that remains read-only and snapshot-driven]

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, multi-client safety, performance, and documentation.

- [ ] T051 [P] Multi-client stress test coverage in `tests/integration/test_websocket_broadcast.py` [Deps: T021, T034, T049] [Output: validated fan-out for two or more simultaneous clients]
- [ ] T052 [P] Graceful reconnect coverage in `tests/integration/test_websocket_broadcast.py` and `client/tests/useWebSocket.test.ts` [Deps: T030, T051] [Output: verified reconnect behavior without simulation corruption]
- [ ] T053 [P] Performance profiling for WebSocket broadcast and render loop in `app/ws/broadcaster.py`, `app/simulation/pathfinding.py`, and `client/src/game/scenes/WorldScene.ts` [Deps: T027, T032, T049] [Output: profiled latency and frame-budget notes for the MVP house scenario]
- [ ] T054 [P] Add tileset license attribution docs in `client/public/assets/tilesets/README.md` and `docs/` as appropriate [Deps: T003] [Output: asset provenance documented for shipped tilesets]
- [ ] T055 Update embodied-world run documentation in `specs/002-embodied-world/quickstart.md`, `README.md`, and `CHANGELOG.md` [Deps: T050, T054] [Output: local run sequence and feature summary documented]
- [ ] T056 Add smoke validation for end-to-end embodied flow in `tests/smoke/test_phase5_embodied_flow.py` [Deps: T034, T042, T049] [Output: automated backend-to-client contract smoke coverage]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: can start immediately.
- **Foundational (Phase 2)**: depends on setup and blocks all user stories.
- **US1 (Phase 3)**: depends on foundational spatial contracts and transport.
- **US2 (Phase 4)**: depends on US1 live transport and foundational spatial modules.
- **US3 (Phase 5)**: depends on US1 live snapshots and foundational replay endpoints.
- **Polish (Phase 6)**: depends on all desired user stories being complete.

### User Story Dependency Graph

- **US1 (P1)** -> **US2 (P2)** -> **US3 (P3)**

### Within Each User Story

- tests for behavior/state/observability first
- schema and contract updates before service logic
- backend authority before frontend rendering polish
- service logic before renderer wiring
- story complete before moving to next priority

### Parallel Opportunities

- Setup and Foundational tasks marked `[P]` can run in parallel where file ownership does not
  overlap.
- US1 tests `T023-T025` can run in parallel.
- US2 tests `T035-T037` can run in parallel.
- US3 tests `T043-T045` can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "Add scenario test for live embodied observation in tests/scenario/test_embodied_scenario.py"
Task: "Add backend/frontend contract test for world snapshot typing in tests/contract/test_websocket_schema.py and client/src/types/world.ts"
Task: "Add frontend hook/unit tests in client/tests/useWebSocket.test.ts and client/tests/useSimulationState.test.ts"
```

## Parallel Example: User Story 2

```bash
Task: "Add scenario test for spatially influenced behavior in tests/scenario/test_embodied_scenario.py"
Task: "Add unit tests for SpatialPerception integration in tests/unit/test_spatial_context.py"
Task: "Add integration test for spatial decision context flow in tests/integration/test_spatial_tick_integration.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add integration test for replay range serving in tests/integration/test_websocket_broadcast.py and tests/integration/test_spatial_tick_integration.py"
Task: "Add frontend replay/control tests in client/tests/useReplay.test.ts and client/tests/timeline.test.ts"
Task: "Add scenario test for replay fidelity in tests/scenario/test_embodied_scenario.py"
```

---

## Critical Path

1. `T002` -> `T004` -> `T013` -> `T014` -> `T015` -> `T018` -> `T019` -> `T021`
2. `T013` -> `T017` -> `T026` -> `T027`
3. `T028` -> `T029` -> `T030` -> `T031` -> `T032` -> `T034`
4. `T038` -> `T039` -> `T040` -> `T041` -> `T042`
5. `T046` -> `T047` -> `T048` -> `T049` -> `T050` -> `T056`

This path is the minimum sequence to reach a working embodied-world MVP with shared map
loading, authoritative live movement, spatial cognition, and replay controls.

---

## Defer For Later

- 3D rendering or physics simulation
- narrative director or story engine
- vector or reflective memory changes
- cloud real-time infrastructure
- auth and multiplayer editing
- procedural map generation
- client-side simulation or predictive movement

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Deliver live shared-map rendering and authoritative sprite movement.
3. Validate browser observation on one small house scenario.
4. Freeze snapshot and tilemap contracts before spatial cognition expansion.

### Incremental Delivery

1. Backend spatial foundation + transport
2. Live observation in Phaser
3. Spatial perception in decisions
4. Replay and controls
5. Polish, docs, and smoke validation

### Single-Developer Agent-Assisted Flow

1. One coding agent handles contracts/tests first.
2. One coding agent handles backend spatial/pathfinding/transport modules.
3. One coding agent handles frontend renderer and hooks.
4. Integrate on shared snapshot contract, then validate replay and docs.

---

## Notes

- `[P]` tasks are parallel-safe when file-level dependencies do not conflict.
- User-story tasks include required `[US#]` labels for traceability.
- The renderer MUST remain read-only throughout implementation.
- Reject changes that move simulation logic or pathfinding into the browser.
- The Streamlit dashboard remains untouched for this feature.
