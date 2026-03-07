# Implementation Plan: Phase 3 Goal-Directed Situated Behavior

**Branch**: `001-behavior-lab-simulation` | **Date**: 2026-03-06 | **Spec**: `C:\Users\akhil\behaviour_lab\specs\001-behavior-lab-simulation\spec.md`
**Input**: Existing feature specification plus the Phase 3 goal-directed behavior request for goals,
needs, resources, zones, interruption handling, and inspectable planning state.

## Summary

Phase 3 extends the completed social simulation into deterministic goal-directed behavior.
Agents keep active goals and intentions across ticks, react to changing needs and local
resources, move through simple zones, and replan when urgent events or shortages override
their current intention. All plan changes, movements, resource events, and need transitions
remain persisted and visible through the API and dashboard.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Streamlit, SQLModel, Pydantic, pydantic-settings, pytest, PyYAML  
**Storage**: SQLite local file database with SQLModel tables for world, planning, and resource state  
**Testing**: pytest unit, integration, scenario, contract, and smoke tests  
**Target Platform**: Local desktop Python runtime on a single machine  
**Project Type**: Monorepo simulation engine + API + dashboard  
**Agent Scale Target**: 2-5 agents in deterministic scenario runs  
**Time Model**: Deterministic tick-based simulation with persisted state snapshots  
**Observability Surface**: Streamlit pages for agents, goals, plans, zones, resources, and timeline;
DB-backed event traces and state tables  
**Performance Goals**: 10-tick, 3-agent, 3-zone scenario under 5 seconds locally including
goal/resource persistence and dashboard queries  
**Constraints**: Local-first, deterministic rule logic first, no LLM planning, no websockets, no auth,
no cloud infra, no microservices, no pygame/2D embodiment in this phase  
**Scale/Scope**: Small situated scenarios with simple zones and 1-3 resource types; no freeform world
simulation or physics engine

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gate Review

- [x] Behavior-first scope: planning, needs, goals, and resource-driven action remain primary; no graphics expansion.
- [x] Python-first simplicity: stack remains unchanged and deterministic rule logic avoids heavy planner frameworks.
- [x] Modular architecture: planning, world state, persistence, dashboard, and simulation extensions remain isolated modules.
- [x] Observable-by-design: goals, intentions, plan changes, movement, acquisitions, consumption, and interruptions will emit structured traces.
- [x] Memory and persona impact: planning consumes memory, persona, relationships, needs, and local context together.
- [x] Communication consequences: communication remains one possible action alongside movement and resource interaction.
- [x] State-over-time continuity: goals, intentions, needs, zone occupancy, and resources persist across ticks.
- [x] Structured schema discipline: goals, plan state, zones, resource records, and plan transitions use structured models.
- [x] Scenario-first validation: Phase 3 introduces a small multi-zone scenario with shortage and interruption pressure.
- [x] Dashboard-first acceptance: goals, needs, resources, zones, and plan transitions must be visible without reading code.
- [x] Local-first baseline: all planning, persistence, and inspection remain local.
- [x] Experiment readiness: deterministic variants can compare how needs/goals/resources shape outcomes.

### Post-Design Gate Review

- [x] Research decisions resolve planning, interruption, and world-grounding ambiguities.
- [x] Data model explicitly covers goals, intentions, needs, zones, resources, and plan-transition events.
- [x] Contracts define goal/plan/resource/zone queries and timeline filtering for new event classes.
- [x] Quickstart demonstrates need -> goal -> plan -> move/resource/social effect visibility.

## Project Structure

### Documentation (this feature)

```text
C:/Users/akhil/behaviour_lab/specs/001-behavior-lab-simulation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api.openapi.yaml
│   └── dashboard-data-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
C:/Users/akhil/behaviour_lab/
├── app/
│   ├── agents/
│   │   ├── decision_policy.py
│   │   ├── planning_policy.py
│   │   ├── relationship_policy.py
│   │   └── models.py
│   ├── api/
│   │   ├── main.py
│   │   ├── schemas/
│   │   └── routes/
│   │       ├── agents.py
│   │       ├── goals.py
│   │       ├── resources.py
│   │       ├── scenarios.py
│   │       ├── simulation.py
│   │       ├── timeline.py
│   │       └── zones.py
│   ├── communication/
│   ├── dashboard/
│   │   ├── main.py
│   │   ├── components/
│   │   └── pages/
│   │       ├── agents.py
│   │       ├── goals.py
│   │       ├── resources.py
│   │       ├── timeline.py
│   │       └── zones.py
│   ├── memory/
│   ├── persistence/
│   │   ├── models.py
│   │   ├── seed.py
│   │   └── repositories/
│   │       ├── social_repository.py
│   │       ├── planning_repository.py
│   │       └── world_repository.py
│   ├── schemas/
│   └── simulation/
│       ├── runner.py
│       ├── scenario_loader.py
│       ├── tick_engine.py
│       └── world_state.py
└── tests/
    ├── contract/
    ├── integration/
    ├── scenario/
    ├── smoke/
    └── unit/
```

**Structure Decision**: Keep the existing single-project monorepo and extend it with dedicated
planning/world repositories, planning policy code, and dashboard pages. This preserves the current
debuggable architecture while adding world-grounded decision state incrementally.

## Phase 0: Outline & Research

### Unknowns Extracted from Technical Context

No unresolved `NEEDS CLARIFICATION` items remain. Phase 3 scope, constraints, and intended world model
are explicit.

### Dependency Best-Practice Research Tasks

- Task: Find best practices for deterministic goal and intention tracking over SQLModel + SQLite.
- Task: Find best practices for modeling zone occupancy and local resource queries in small simulations.
- Task: Find best practices for representing lightweight need/drive state without exploding rule complexity.

### Integration Pattern Research Tasks

- Task: Find patterns for urgent-event interruption logic layered on top of a deterministic tick loop.
- Task: Find patterns for plan-change event tracing that remain replayable in dashboards.
- Task: Find patterns for combining social context with location/resource context in transparent rule policies.

## Phase 1: Design & Contracts

### Phase 3 Repository/Module Changes

- `agents/`: add planning policy and goal-selection helpers; extend state and persona influence rules.
- `simulation/`: upgrade tick flow to support plan persistence, movement, location checks, resource actions,
  and interruption handling.
- `persistence/`: add goal/intention, zone/location, resource, and occupancy/resource-event models with repositories.
- `api/routes/`: expose goal, intention, zone, and resource views plus replanning-related timeline data.
- `dashboard/pages/`: add or extend goals, resources, zones, agent-state, and timeline views for plan observability.
- `configs/`: add a deterministic multi-zone scenario with resources, starting locations, and urgent events.

### Why This Architecture Fits Phase 3

- Extends the deterministic social loop instead of replacing it, preserving trust in existing tests and replayability.
- Adds simple world grounding through zones rather than full movement/physics, which matches the constitution.
- Keeps goals, plans, needs, and resource changes as structured tables and events, which is easier to debug than
  opaque planner outputs.
- Preserves dashboard-as-source-of-inspection by making world and plan changes persisted first, rendered second.

### New/Updated Models and Services

- **Goal**
  - Tracks persisted goal type, priority, status, target, urgency source, and owning agent.
- **PlanState / Intention**
  - Tracks the agent's active intention, current action type, status, rationale, interruptibility, and zone/resource target.
- **AgentStateSnapshot extension**
  - Adds `hunger`, `safety_need`, `social_need`, `zone_id`, and lightweight inventory/resource counters.
- **Zone**
  - Represents simple named locations with zone type and metadata.
- **Resource**
  - Represents scenario resources located in zones with quantity and status.
- **ResourceEvent**
  - Captures acquire, consume, move, shortage, and replenish effects either as a dedicated table or structured event subtype.
- **Services**
  - `planning_policy`
  - `goal_service`
  - `world_repository`
  - `resource_service`
  - `interruption_policy`

### End-to-End Data Flow (Phase 3)

1. Tick begins with recent global and local events, current zone occupancy, resource availability, memory, and relationship context.
2. Agent reads active needs and any existing goal/intention state.
3. Planning policy decides to continue, defer, switch, or interrupt the current plan.
4. If movement is needed, the agent changes zone and persists movement events and state snapshot updates.
5. If resource interaction is available, the agent acquires or consumes resources and persists inventory/resource events.
6. If social interaction remains appropriate, the agent communicates or cooperates using existing Phase 2 mechanics.
7. Goal/intention updates, decision logs, memory traces, and resulting SimulationEvents are persisted.
8. Dashboard reads goals, needs, resources, zones, and timeline traces directly from persisted state.

### Slice-by-Slice Roadmap Within Phase 3

- **Slice A: Goal and Need Persistence**
  - Add goal/intention models, agent state need fields, and persisted planning status.
- **Slice B: Zones and Resource Grounding**
  - Add zones, agent location, resource state, and location-aware opportunity checks.
- **Slice C: Deterministic Planning Loop**
  - Add planning policy that continues, defers, switches, or interrupts plans using needs + local context.
- **Slice D: Resource and Movement Actions**
  - Implement `move`, `acquire`, and `consume` actions with persisted events and state changes.
- **Slice E: Dashboard Observability**
  - Add goals/plans, zone occupancy, and resource views with new timeline filters and causal visibility.
- **Slice F: Validation Scenarios**
  - Add shortage and urgent-event scenarios to prove interruption, replanning, and goal persistence.

### Risks, Tradeoffs, and What to Avoid

- Risk: planning state becomes opaque and hard to trust.
  - Mitigation: persist every plan change and interruption as explicit events with rationale.
- Risk: world grounding grows into premature game logic.
  - Mitigation: limit Phase 3 to zone transitions and simple resource tables; no pathfinding or physics.
- Risk: too many need variables produce brittle heuristics.
  - Mitigation: keep initial needs minimal (`hunger`, `safety_need`, optional `social_need`) and deterministic.
- Avoid:
  - LLM planning in this phase.
  - Full 2D/pygame embodiment.
  - Vector memory or distributed world simulation.
  - Hidden in-memory plan state not mirrored to the database.

### Acceptance Criteria for Phase 3 Completion

- Agents persist current goals and active intentions across ticks.
- Agents can move between zones and resource opportunities depend on location.
- Resource shortage changes decisions and can redirect agent plans.
- Urgent events or severe needs can interrupt an active plan and create persisted plan-change events.
- Dashboard shows goals, needs, plans, locations, resources, and timeline traces for plan transitions.
- Timeline supports causal inspection across need -> goal -> intention -> action -> world/social effect.
- Phase 3 scenario tests pass locally and remain deterministic across reruns.

## Complexity Tracking

No constitutional violations currently require exceptions.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
