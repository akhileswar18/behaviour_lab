# Feature Specification: Phase 5 2D Embodied Simulation World

**Feature Branch**: `[002-embodied-world]`
**Created**: 2026-03-19
**Status**: Draft
**Input**: User description: "Phase 5 — 2D Embodied Simulation World"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Watch Agents Live (Priority: P1)

A researcher opens the browser, sees a pixel-art house, watches agents walk between rooms,
sees floating name labels and action indicators, and can click an agent to inspect their
current state in a side panel while the simulation continues to run.

**Why this priority**: Real-time embodied observation is the smallest valuable slice of the
feature and proves that the new renderer can mirror backend state without taking over
simulation logic.

**Independent Test**: Can be fully tested by running a three-agent scenario for ten ticks,
opening the browser client, and verifying that agent positions, room transitions, labels,
and side-panel state update from backend broadcasts.

**Acceptance Scenarios**:

1. **Given** a seeded house scenario with three agents and a running backend, **When** the
   researcher opens the browser client, **Then** the tilemap, agent sprites, room layout,
   and current tick appear without reading hidden in-memory state.
2. **Given** agents moving between kitchen, bedroom, and living room, **When** ticks
   advance, **Then** the canvas shows each room transition, movement path, and current room
   within two seconds of the authoritative tick completing.
3. **Given** the researcher clicks one agent sprite, **When** the side panel opens,
   **Then** it shows that agent's current needs, active goal, recent decisions, and live
   conversation context.

---

### User Story 2 - Spatial Grounding for Agent Cognition (Priority: P2)

The tick engine includes tile-level spatial context in agent perception so agents reason
about exact position, room membership, nearby agents and objects, and movement cost to
targets rather than moving only by abstract zone names.

**Why this priority**: Embodied observation is useful, but the real research value comes
when space changes behavior rather than only decorating it.

**Independent Test**: Can be fully tested by running a scenario where at least one hungry
agent chooses a kitchen path because food is spatially located there and the resulting path
is visible both in traces and in the renderer.

**Acceptance Scenarios**:

1. **Given** a hungry agent in the living room and food located in the kitchen, **When**
   the tick engine evaluates the next action, **Then** the decision context includes current
   room, nearby objects, and pathfinding cost to the kitchen and the chosen action uses that
   spatial information.
2. **Given** two agents are near one another in the same room, **When** a communication or
   cooperation action is selected, **Then** the decision context reflects their spatial
   proximity and the resulting interaction is visible in both world events and renderer
   overlays.
3. **Given** a zone-based scenario with no tilemap configured, **When** the simulation runs,
   **Then** existing zone behavior continues unchanged and tile coordinates remain nullable.

---

### User Story 3 - Replay and Observation Controls (Priority: P3)

A researcher can pause the viewer, scrub the timeline to historical ticks, replay the world
at multiple speeds, and optionally follow one agent while inspecting past world state.

**Why this priority**: Replay and controls deepen analysis, but they depend on live viewing
and spatial state contracts already being stable.

**Independent Test**: Can be fully tested by requesting a stored tick range, replaying it in
the client at 1x, 2x, and 5x, and verifying that the renderer shows the correct historical
positions and side-panel state.

**Acceptance Scenarios**:

1. **Given** a completed ten-tick run, **When** the researcher scrubs to tick 4,
   **Then** the canvas and side panel show the world state persisted for tick 4 rather than
   the latest live state.
2. **Given** replay mode is active, **When** the researcher changes playback speed,
   **Then** the renderer advances through stored snapshots at the selected rate without
   modifying backend simulation state.
3. **Given** one agent is selected during replay, **When** follow-camera mode is enabled,
   **Then** the camera tracks that agent while preserving the authoritative replay snapshot
   order.

### Edge Cases

- What happens when no browser clients are connected during a running simulation?
- How does the system handle a browser client disconnecting and reconnecting mid-run?
- What happens when a scenario has no configured tilemap and only zone-based state exists?
- How does the system handle a malformed Tiled JSON file or a tilemap the backend can parse
  but the renderer cannot render?
- What happens when two agents target the same doorway or tile corridor at the same time?
- How does the system handle replay requests outside the stored tick range?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a separate browser-based Phaser 3 plus React client for
  embodied world observation.
- **FR-002**: The browser client MUST render a tile-based house with 3-5 rooms using a Tiled
  JSON map and 16x16 pixel-art tiles displayed at 3x scale with pixel-art rendering enabled.
- **FR-003**: The backend MUST remain authoritative for all simulation logic, decisions,
  state mutation, pathfinding, and persistence.
- **FR-004**: The renderer MUST be read-only and MUST communicate with the backend only
  through FastAPI WebSocket and REST.
- **FR-005**: The backend MUST broadcast a structured `tick_update` snapshot to all connected
  WebSocket clients for each completed tick.
- **FR-006**: The browser client MUST render agent sprites, room transitions, name labels,
  current action indicators, and mood indicators from authoritative snapshots.
- **FR-007**: The browser client MUST show speech bubbles, thought clouds, or equivalent
  overlays when conversation, thought, or interaction data is present in the snapshot.
- **FR-008**: The browser client MUST support click-to-select on agent sprites and display
  the selected agent's needs, goal, recent decisions, and conversation context in a side
  panel.
- **FR-009**: The client MUST support Play, Pause, and playback speed controls for live and
  replay observation.
- **FR-010**: The system MUST support replay by serving historical world snapshots for a
  requested tick range through REST and rendering them in the browser client.
- **FR-011**: The browser client MUST support camera pan, zoom, and optional follow-camera
  mode for a selected agent.
- **FR-012**: The browser client SHOULD render a minimap and day/night overlay when the
  required data is present without changing backend simulation rules.
- **FR-013**: The backend MUST load the same Tiled JSON map used by the client and derive
  collision data, room boundaries, object affordances, and zone mappings from it.
- **FR-014**: The backend MUST compute A* paths on the tile collision grid for movement
  actions and persist resulting tile coordinates in agent state snapshots.
- **FR-015**: The decision engine MUST receive spatial context including current tile,
  current room, nearby agents, nearby objects, and pathfinding cost to relevant targets.
- **FR-016**: The system MUST preserve backward compatibility for zone-only scenarios by
  treating tile coordinates and map bindings as optional.
- **FR-017**: REST endpoints MUST serve tilemap metadata, replay ranges, and any other heavy
  or infrequent payloads that do not belong in per-tick WebSocket messages.
- **FR-018**: The WebSocket contract MUST be versioned and support graceful connection,
  reconnection, and multi-client observation.
- **FR-019**: The simulation MUST continue to run correctly if every renderer client
  disconnects.
- **FR-020**: The existing Streamlit dashboard MUST remain untouched and continue to operate
  from persisted data exactly as before.

### Key Entities *(include if feature involves data)*

- **TileMap**: Structured Tiled JSON map describing rooms, layers, collision tiles, object
  affordances, and zone mapping.
- **TilePosition**: Integer tile coordinates (`tile_x`, `tile_y`) representing an agent's
  authoritative location on the grid.
- **SpatialContext**: Backend-computed perception payload including current room, nearby
  agents, nearby objects, visible resources, and pathfinding costs.
- **AgentSprite**: Renderer-side representation of an agent with authoritative identity,
  current position, visual state, and interpolation state.
- **WorldSnapshot**: Versioned per-tick broadcast payload containing simulation time, world
  state, agent positions, actions, overlays, and interactions.
- **PathSegment**: Ordered server-computed tile waypoints for a movement action.
- **ConversationBubble**: Visual overlay payload describing speech or thought text, target,
  duration, and source agent.

### Assumptions

- The initial embodied world targets small scenarios with 2-5 agents inside a house-scale
  tilemap rather than large outdoor worlds.
- Tilemaps are static files versioned with the repository and loaded locally by both backend
  and client.
- The browser client is additive and does not replace the Streamlit observability workflow.
- Replay is based on persisted historical tick state rather than speculative re-simulation in
  the browser.

## Constitution Alignment *(mandatory)*

- **I. Behavior-First Over Graphics-First**: The feature uses graphics only to ground and
  observe agent behavior; all simulation rules remain in Python.
- **II. Python-First Simplicity**: Backend spatial logic uses lightweight JSON parsing and a
  small in-repo A* implementation instead of heavy engine dependencies.
- **III. Modular Agent Architecture**: Cognition, world, renderer, WebSocket transport, and
  persistence are split into explicit backend and frontend modules.
- **IV. Observable by Design**: Tile positions, movement paths, room transitions, speech
  overlays, and snapshot broadcasts remain structured and traceable.
- **V. Memory Is a First-Class System**: The embodied world surfaces memory-driven behavior
  visually without changing memory's role as a backend subsystem.
- **VI. Persona Must Influence Behavior**: Persona and needs continue to shape movement,
  proximity interactions, and action selection in space.
- **VII. Communication Must Change State**: Conversations shown in bubbles and side panels
  still originate from state-changing communication events in the backend.
- **VIII. Dashboard-and-World-First Validation**: Spatial features validate through the
  Phaser world while cognition and memory remain inspectable in dashboard traces.
- **IX. Scenario-Driven Iteration**: The initial house scenario is a bounded 3-5 room world
  with 2-5 agents and explicit validation slices.
- **X. State and Time Matter**: Tile positions and replay snapshots extend the existing
  tick-based continuity model.
- **XI. Structured Data Over Ad Hoc Text Blobs**: Tilemaps, spatial context, and WebSocket
  snapshots use structured contracts rather than renderer-specific free text.
- **XII. Fast Iteration With Safety Rails**: The browser client remains additive and
  read-only, protecting backend stability while enabling incremental slices.
- **XIII. Local-First Development**: The backend, Vite client, tilemap files, and replay
  workflows all run locally without required cloud services.
- **XIV. Experiment-Friendly Design**: Different room layouts, affordances, and spatial
  settings can be compared without replacing the core simulation.
- **XV. Incremental Complexity**: The feature introduces space in phases: map loading,
  movement sync, spatial perception, then replay and polish.
- **XVI. Code Quality for AI-Assisted Development**: The feature uses typed schemas,
  versioned contracts, and strict module boundaries across backend and frontend.
- **XVII. Milestone Success Criteria**: The feature extends the validated social and memory
  loop rather than replacing it, preserving prior milestone behavior.
- **XVIII. Embodied Spatial World as Behavioral Grounding**: The feature directly implements
  optional tile-based space, room mapping, object affordances, and backend-persisted tile
  coordinates.
- **XIX. Renderer Is a Read-Only Observer**: The Phaser plus React client renders and
  interpolates only; decisions, pathfinding, and state changes remain in Python.
- **XX. WebSocket-First Real-Time Communication**: Live world state uses versioned WebSocket
  snapshots and replay/tilemap data use REST.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A 3-agent scenario runs 10 ticks and all agent positions, movements, and room
  transitions are visible in the Phaser canvas within 2 seconds of each tick completing.
- **SC-002**: Clicking an agent shows their needs, goal, recent decisions, and conversation
  in the side panel.
- **SC-003**: At least one decision in a 10-tick run is demonstrably influenced by spatial
  context, such as a hungry agent pathing to the kitchen because food is located there, and
  the visible path matches the backend trace.
- **SC-004**: Replay mode can scrub to any stored past tick in the requested range and
  render the correct world state for that historical point.
- **SC-005**: Simulation continues running if the browser client disconnects and reconnects.
