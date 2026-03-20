# Research: Phase 5 2D Embodied Simulation World

## Decision 1: Load Tiled JSON with built-in Python parsing

- Decision: Use Python's built-in `json.load` plus a custom parser in
  `app/simulation/tilemap_loader.py` for Tiled JSON files.
- Rationale: The tilemaps are static repository assets, so a custom parser avoids extra
  dependencies and keeps the backend easy to reason about.
- Alternatives considered:
  - A dedicated Tiled Python library: rejected because it adds weight without solving a
    complex parsing problem for the MVP.
  - Hardcoded map structures in Python: rejected because the constitution requires shared map
    data interpretable by backend and renderer.

## Decision 2: Use a lightweight pure-Python A* implementation

- Decision: Implement A* directly in `app/simulation/pathfinding.py` for the indoor 40x30
  collision grid.
- Rationale: The grid is small and deterministic, so a compact in-repo implementation stays
  fast enough and avoids external graph libraries.
- Alternatives considered:
  - NetworkX or another graph library: rejected as unnecessary dependency overhead.
  - Client-side pathfinding: rejected because the renderer must remain read-only.

## Decision 3: Use FastAPI native WebSocket broadcasting with a connection manager

- Decision: Implement WebSocket fan-out with FastAPI's built-in `WebSocket` support and a
  connection manager in `app/ws/broadcaster.py`.
- Rationale: Native FastAPI WebSockets are sufficient for local multi-client observation and
  preserve a simple Python-first stack.
- Alternatives considered:
  - Redis pub/sub or external socket broker: rejected because local-first MVP does not need
    extra infrastructure.
  - Polling REST for live ticks: rejected because it adds latency and weakens the real-time
    viewing experience.

## Decision 4: Map zones to rooms through Tiled object-layer metadata

- Decision: Use rectangle objects in a Tiled object layer with a required `zone` custom
  property to map rooms or areas to existing `Zone` records.
- Rationale: This keeps zone compatibility explicit and editable in map design tools without
  hardcoding backend geometry.
- Alternatives considered:
  - Infer zones from tile indices or layers alone: rejected because it is brittle and opaque.
  - Store room geometry only in SQLite: rejected because backend and client must share the
    same map interpretation.

## Decision 5: Use snapshot interpolation on the client

- Decision: Buffer previous and current authoritative tick snapshots in the browser and
  linearly interpolate sprite positions between them at render time.
- Rationale: Interpolation produces smooth 60fps motion without giving the client authority
  to predict or alter future state.
- Alternatives considered:
  - Teleport sprites directly per tick: rejected because it creates unreadable movement.
  - Client prediction: rejected because it violates the server-authoritative renderer rule.

## Decision 6: Extend AgentStateSnapshot with nullable tile coordinates

- Decision: Add nullable `tile_x` and `tile_y` columns to `AgentStateSnapshot`.
- Rationale: The extension preserves backward compatibility with zone-only scenarios while
  allowing embodied scenarios to persist authoritative positions per tick.
- Alternatives considered:
  - Create a separate spatial position table: rejected because position is part of state
    continuity and belongs with the tick snapshot.
  - Make tile coordinates mandatory: rejected because current scenarios must keep working
    without tilemaps.
