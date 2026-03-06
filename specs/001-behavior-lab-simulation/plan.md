# Implementation Plan: Phase 2 Social Dynamics for Multi-Agent Behavior Lab

**Branch**: `001-behavior-lab-simulation` | **Date**: 2026-03-06 | **Spec**: `C:\Users\akhil\behaviour_lab\specs\001-behavior-lab-simulation\spec.md`
**Input**: Feature specification from `C:\Users\akhil\behaviour_lab\specs\001-behavior-lab-simulation\spec.md` and Phase 2 objective request.

## Summary

Phase 1 is complete and provides a runnable local baseline. Phase 2 extends the existing tick loop into
real social dynamics: structured agent-to-agent communication, explicit relationship updates, persona-driven
behavior differences, and scenario/world event influence. All effects remain persisted and inspectable via
FastAPI + Streamlit without introducing cloud, websocket, or distributed complexity.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Streamlit, SQLModel, Pydantic, pydantic-settings, pytest
**Storage**: SQLite (local single-file persistent state)
**Testing**: pytest (unit + integration + scenario + contract)
**Target Platform**: Local desktop runtime (single machine)
**Project Type**: Single-project monorepo with API, simulation engine, and dashboard
**Agent Scale Target**: 2-5 agents per scenario for deterministic social behavior studies
**Time Model**: Deterministic tick-based orchestration with persisted per-tick outputs
**Observability Surface**: Streamlit social views + structured DB-backed timeline/event/message traces
**Performance Goals**: 10-tick, 3-agent scenario under 5 seconds locally with full event persistence
**Constraints**: Local-first, deterministic logic first, no websockets, no auth, no cloud, no microservices
**Scale/Scope**: Social behavior depth over scale; incremental extension of current loop, not a rewrite

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gate Review

- [x] Behavior-first scope: work targets communication, persona, memory, relationships, and inspectability.
- [x] Python-first simplicity: stack unchanged; no heavy new frameworks.
- [x] Modular architecture: extends existing modules (`communication`, `simulation`, `memory`, `dashboard`, `persistence`).
- [x] Observable-by-design: message, relationship, and scenario event transitions are persisted and queryable.
- [x] Memory and persona impact: decision pipeline consumes persona traits + memory retrieval context.
- [x] Communication consequences: messages trigger relationship and memory side effects.
- [x] State-over-time continuity: all social updates tied to tick timeline.
- [x] Structured schema discipline: Message/Relationship/SimulationEvent payloads remain structured.
- [x] Scenario-first validation: triad scenario and event injection validate social interactions.
- [x] Dashboard-first acceptance: dedicated communication/relationship/agent-detail timeline views required.
- [x] Local-first baseline: no new external runtime dependencies.
- [x] Experiment readiness: run-to-run comparison remains available and expanded with social metrics.

### Post-Design Gate Review (after Phase 1 artifacts)

- [x] Research decisions resolve all architecture ambiguities.
- [x] Data model explicitly covers message intent/tone, relationship score evolution, and scenario event injection.
- [x] Contracts define communication feed, relationship history, event injection, and filtered timeline access.
- [x] Quickstart demonstrates end-to-end social flow: event -> message -> relationship update -> memory trace.

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
│   ├── api/
│   │   ├── main.py
│   │   └── routes/
│   │       ├── scenarios.py
│   │       ├── simulation.py
│   │       ├── timeline.py
│   │       ├── agents.py
│   │       └── relationships.py
│   ├── agents/
│   │   ├── models.py
│   │   └── decision_policy.py
│   ├── communication/
│   │   ├── models.py
│   │   ├── message_bus.py
│   │   └── handlers.py
│   ├── memory/
│   │   ├── writer.py
│   │   ├── retriever.py
│   │   └── summarizer.py
│   ├── simulation/
│   │   ├── runner.py
│   │   ├── tick_engine.py
│   │   ├── world_state.py
│   │   └── scenario_loader.py
│   ├── persistence/
│   │   ├── models.py
│   │   └── repositories/
│   └── dashboard/
│       ├── main.py
│       ├── components/
│       └── pages/
└── tests/
    ├── unit/
    ├── integration/
    ├── scenario/
    └── contract/
```

**Structure Decision**: Keep the current monorepo and extend existing modules in-place to preserve
local debuggability and avoid architectural churn.

## Phase 0: Outline & Research

### Unknowns Extracted from Technical Context

No unresolved `NEEDS CLARIFICATION` items remain. Phase 2 scope and constraints are explicit.

### Dependency Best-Practice Research Tasks

- Task: Find best practices for deterministic social-interaction simulation over SQLModel+SQLite.
- Task: Find best practices for modeling relationship score updates with auditable event traces.
- Task: Find best practices for keeping Streamlit social dashboards query-driven from persisted state.

### Integration Pattern Research Tasks

- Task: Find patterns for event injection into tick loops without breaking determinism.
- Task: Find patterns for message -> relationship -> memory side-effect chains with traceability.
- Task: Find patterns for persona trait influence that remains explainable in decision logs.

## Phase 1: Design & Contracts

### Phase 2 Repository/Module Changes

- `communication/`: Add explicit message intent, emotional tone, and addressing modes.
- `simulation/`: Extend tick flow to include scenario event ingestion and social action policies.
- `agents/`: Expand persona influence factors (cooperation/risk/communication style/memory sensitivity).
- `persistence/`: Ensure structured columns for social payloads and relationship timelines.
- `api/routes/`: Add/extend endpoints for social message feeds, relationship history, event injection.
- `dashboard/pages/`: Improve communication feed, relationship tables, agent detail explainability, filters.

### Why This Architecture Fits Phase 2

- Extends current loop instead of replacing it, preserving momentum and test coverage.
- Keeps deterministic behavior for reproducible experiments.
- Maintains clean module boundaries for future policy swaps.
- Uses persisted state as source of truth for dashboard inspectability.

### New/Updated Models and Services

- **Message**:
  - Add/confirm fields: `intent`, `emotional_tone`, `tick_number`, `sender_agent_id`, `receiver_agent_id|broadcast`.
- **Relationship**:
  - Add/confirm fields: `trust_score`, `affinity_score|stance`, `last_interaction_at`, `updated_at`.
- **SimulationEvent**:
  - Ensure structured `event_type`, `actor_agent_id`, `target_agent_id`, `scenario_id`, `tick_number`, `payload`.
- **PersonaProfile**:
  - Add/confirm: `cooperation_tendency`, `risk_tolerance`, `communication_style`, `memory_sensitivity`, optional `emotional_bias`.
- **Services**:
  - `message_service`, `relationship_update_service`, `scenario_event_injection_service`, `decision_explainer`.

### End-to-End Data Flow (Phase 2)

1. Scenario/world events are loaded or injected for current tick.
2. Agent observes recent SimulationEvents and retrieves relevant memory.
3. Decision policy combines persona + relationship context + world state.
4. Agent chooses social action (`communicate`, `cooperate`, `avoid`, `warn`, `propose`, `wait`).
5. Persist DecisionLog with rationale fields.
6. If communication occurs, persist Message + corresponding SimulationEvent.
7. Apply relationship update rule and persist Relationship + relationship_update event.
8. Create resulting memory records and retrieval traces.
9. Dashboard reads persisted state and renders message->relationship->memory chain.

### Slice-by-Slice Roadmap Within Phase 2

- **Slice A: Message Flow Foundation**
  - Structured message creation + persistence + communication feed API + dashboard feed view.
- **Slice B: Relationship Dynamics**
  - Relationship update rules and persistence; relationship history API + dashboard relationship table/graph proxy.
- **Slice C: Persona Influence Expansion**
  - Persona trait normalization and policy weighting; decision logs include influence explanation.
- **Slice D: Scenario Event Layer**
  - Introduce deterministic scenario event injection and tie events to social decisions.
- **Slice E: Explainability and Traceability**
  - Ensure decision logs and timeline show causal chain across world event, message, relationship, memory.
- **Slice F: Validation and Stabilization**
  - Scenario and integration tests for social dynamics; local demo script and acceptance verification.

### Risks, Tradeoffs, and What to Avoid

- Risk: Non-deterministic behavior reduces debugability.
  - Mitigation: deterministic policy defaults and fixed per-tick ordering.
- Risk: Relationship updates become opaque heuristics.
  - Mitigation: explicit rule definitions + event-level trace payloads.
- Risk: Dashboard over-couples to in-memory state.
  - Mitigation: all views query persisted models only.
- Avoid:
  - Adding LLM integration in this phase (future work only).
  - Rewriting existing architecture or introducing microservices.
  - Introducing websocket push complexity before needs are proven.
  - Adding vector DB memory or movement/game-world mechanics.

### Acceptance Criteria for Phase 2 Completion

- Agents can send persisted messages with intent/tone metadata.
- Dashboard communication feed shows ordered messages with scenario/agent/tick filters.
- Relationship state updates are persisted and visible after interactions.
- Decision logs include persona + relationship + scenario-event rationale signals.
- Scenario/world events can be injected and affect agent actions in subsequent ticks.
- Timeline clearly exposes causal chain: world event -> decision/message -> relationship change -> memory.
- All Phase 2 tests pass locally with reproducible outputs.

## Complexity Tracking

No constitutional violations currently require exceptions.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
