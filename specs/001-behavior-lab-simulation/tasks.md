# Tasks: Phase 3 Goal-Directed Situated Behavior

**Input**: Design documents from `C:/Users/akhil/behaviour_lab/specs/001-behavior-lab-simulation/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Test tasks are included because Phase 3 requires deterministic planning, persisted state transitions,
and dashboard-observable world/resource behavior.

**Organization**: Tasks are grouped by user story to keep each increment independently implementable and testable.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Parallelizable task (different file or isolated implementation surface)
- **[Story]**: Appears only in user-story phases (`[US1]`, `[US2]`, `[US3]`)

## Phase 1: Setup (Phase 3 Baseline)

**Purpose**: Prepare the codebase for Phase 3 world-grounded planning work without changing the overall architecture.

- [X] T001 Align Phase 3 dependencies and optional dev tooling in C:/Users/akhil/behaviour_lab/pyproject.toml (Output: reproducible dependency set for goals/resources/zones work)
- [X] T002 Extend deterministic planning/runtime settings in C:/Users/akhil/behaviour_lab/app/schemas/settings.py (Output: config flags for need progression, interruption thresholds, and zone/resource behavior)
- [X] T003 [P] Add Phase 3 social-world schemas and enums in C:/Users/akhil/behaviour_lab/app/schemas/social.py (Output: shared enums for goals, intention status, zones, resources, and event types)
- [X] T004 [P] Add Phase 3 seeded scenario config in C:/Users/akhil/behaviour_lab/app/configs/scenarios/sample_goal_resource_lab.yaml (Output: multi-zone deterministic scenario with scarce resource and urgent event)
- [X] T005 [P] Update agent seed config with need/goals-ready persona defaults in C:/Users/akhil/behaviour_lab/app/configs/agents/sample_agents.yaml (Output: personas compatible with Phase 3 planning inputs)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema, repositories, and shared world/planning infrastructure required before any user story implementation.

**CRITICAL**: No user story work begins until this phase is complete.

- [X] T006 Extend persisted models for goals, intentions, zones, resources, and Phase 3 state fields in C:/Users/akhil/behaviour_lab/app/persistence/models.py (Depends on: T001,T003; Output: SQLModel entities and state extensions)
- [X] T007 Apply DB initialization updates and indexes for Phase 3 entities in C:/Users/akhil/behaviour_lab/app/persistence/init_db.py (Depends on: T006; Output: local DB schema support for world/planning tables)
- [X] T008 [P] Add planning repository primitives in C:/Users/akhil/behaviour_lab/app/persistence/repositories/planning_repository.py (Depends on: T006; Output: CRUD/query layer for goals and intentions)
- [X] T009 [P] Add world repository primitives in C:/Users/akhil/behaviour_lab/app/persistence/repositories/world_repository.py (Depends on: T006; Output: CRUD/query layer for zones, resources, and occupancy)
- [X] T010 [P] Add API schemas for goals, intentions, zones, and resources in C:/Users/akhil/behaviour_lab/app/api/schemas/social.py (Depends on: T003,T006; Output: typed response/request models for new endpoints)
- [X] T011 [P] Extend scenario seeding for zones, resources, and starting locations in C:/Users/akhil/behaviour_lab/app/persistence/seed.py (Depends on: T004,T005,T006; Output: seeded Phase 3 world state)
- [X] T012 Add shared integration fixture for Phase 3 seeded scenarios in C:/Users/akhil/behaviour_lab/tests/conftest.py (Depends on: T007,T011; Output: reusable test fixture for Phase 3 integration/scenario tests)

**Checkpoint**: Foundation complete; user-story work can begin.

---

## Phase 3: User Story 1 - Run a Goal-Directed Situated Scenario (Priority: P1) MVP

**Goal**: Agents maintain explicit goals and active intentions, react to needs and local world context, and execute deterministic plan-driven actions across ticks.

**Independent Test**: Seed a 3-agent, 3-zone scenario, run 10 ticks, and verify at least one agent persists a goal/intention across ticks, moves zones, and changes behavior due to needs or resource context.

### Tests for User Story 1

- [X] T013 [P] [US1] Add contract test for goals/intentions endpoints in C:/Users/akhil/behaviour_lab/tests/contract/test_goals_contract.py (Depends on: T010; Output: locked contract for goal and intention responses)
- [X] T014 [P] [US1] Add integration test for goal/intention persistence and transitions in C:/Users/akhil/behaviour_lab/tests/integration/test_goal_intention_persistence.py (Depends on: T012; Output: verified active/deferred/interrupted/completed transitions)
- [X] T015 [P] [US1] Add scenario test for deterministic need-driven action divergence in C:/Users/akhil/behaviour_lab/tests/scenario/test_need_driven_planning.py (Depends on: T012; Output: reproducible behavior difference under different need levels)

### Implementation for User Story 1

- [X] T016 [US1] Implement goal/intention model helpers and state transitions in C:/Users/akhil/behaviour_lab/app/agents/models.py (Depends on: T006; Output: in-code planning state structures aligned with persisted models)
- [X] T017 [US1] Implement planning policy for continue/defer/switch behavior in C:/Users/akhil/behaviour_lab/app/agents/planning_policy.py (Depends on: T008,T016; Output: deterministic goal and intention selection logic)
- [X] T018 [US1] Extend persona/state decision inputs with hunger and safety/social needs in C:/Users/akhil/behaviour_lab/app/agents/decision_policy.py (Depends on: T016,T017; Output: decision policy accepts need and intention context)
- [X] T019 [US1] Persist seeded goals and initial active intentions in C:/Users/akhil/behaviour_lab/app/persistence/seed.py (Depends on: T011,T017; Output: agents start with explicit goals/intention state)
- [X] T020 [US1] Add goals and intentions query/service methods in C:/Users/akhil/behaviour_lab/app/persistence/repositories/planning_repository.py (Depends on: T008; Output: repository support for active/history planning state)
- [X] T021 [US1] Add goals and intentions API endpoints in C:/Users/akhil/behaviour_lab/app/api/routes/goals.py (Depends on: T010,T020; Output: `GET /scenarios/{id}/goals` and `GET /scenarios/{id}/intentions`)
- [X] T022 [US1] Extend tick loop with need progression and goal/intention evaluation in C:/Users/akhil/behaviour_lab/app/simulation/tick_engine.py (Depends on: T017,T018,T020; Output: goal-driven per-tick planning updates)
- [X] T023 [US1] Emit `plan_change` and threshold-crossing events in C:/Users/akhil/behaviour_lab/app/simulation/tick_engine.py (Depends on: T022; Output: persisted planning/need events in the timeline)
- [X] T024 [US1] Update agent detail dashboard to show needs, active goal, and active intention in C:/Users/akhil/behaviour_lab/app/dashboard/pages/agents.py (Depends on: T021,T022; Output: inspectable agent planning state)
- [X] T025 [US1] Add goals and intentions dashboard page in C:/Users/akhil/behaviour_lab/app/dashboard/pages/goals.py (Depends on: T021; Output: dedicated Phase 3 planning view)
- [X] T026 [US1] Register goals page access in C:/Users/akhil/behaviour_lab/app/dashboard/main.py (Depends on: T025; Output: navigable Phase 3 planning page)
- [X] T027 [US1] Update story-level run steps for goals and needs in C:/Users/akhil/behaviour_lab/specs/001-behavior-lab-simulation/quickstart.md (Depends on: T021,T024; Output: executable US1 validation steps)

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Inspect Resources, Zones, and Plan Interruptions (Priority: P2)

**Goal**: World context becomes situated through zones/resources, and urgent conditions can interrupt and redirect plans with persisted causal traces.

**Independent Test**: Run a scenario with scarce food and an urgent safety event; verify at least one agent moves zones, acquires/consumes a resource, and persists an interruption or replanning event explaining the switch.

### Tests for User Story 2

- [X] T028 [P] [US2] Add contract test for zones/resources endpoints in C:/Users/akhil/behaviour_lab/tests/contract/test_world_contract.py (Depends on: T010; Output: locked contract for zone and resource queries)
- [X] T029 [P] [US2] Add integration test for resource acquire/consume/shortage cases in C:/Users/akhil/behaviour_lab/tests/integration/test_resource_flow.py (Depends on: T012; Output: verified resource state transitions)
- [X] T030 [P] [US2] Add scenario test for interruption and replanning flow in C:/Users/akhil/behaviour_lab/tests/scenario/test_interruption_replanning.py (Depends on: T012,T023; Output: deterministic interruption behavior under urgent conditions)

### Implementation for User Story 2

- [X] T031 [US2] Implement zone and resource query logic in C:/Users/akhil/behaviour_lab/app/persistence/repositories/world_repository.py (Depends on: T009; Output: local world data access for planning loop and API)
- [X] T032 [US2] Extend world context builder with zones, local resources, and occupancy in C:/Users/akhil/behaviour_lab/app/simulation/world_state.py (Depends on: T009,T031; Output: zone-aware tick context)
- [X] T033 [US2] Implement deterministic move/acquire/consume action handlers in C:/Users/akhil/behaviour_lab/app/simulation/tick_engine.py (Depends on: T022,T031,T032; Output: persisted resource and movement actions)
- [X] T034 [US2] Implement interruption policy for urgent events and severe needs in C:/Users/akhil/behaviour_lab/app/agents/planning_policy.py (Depends on: T017,T032; Output: explicit continue vs interrupt vs replan logic)
- [X] T035 [US2] Persist movement, resource, and interruption events with rationale in C:/Users/akhil/behaviour_lab/app/simulation/tick_engine.py (Depends on: T033,T034; Output: auditable Phase 3 event stream)
- [X] T036 [US2] Add zones endpoint in C:/Users/akhil/behaviour_lab/app/api/routes/zones.py (Depends on: T010,T031; Output: `GET /scenarios/{id}/zones`)
- [X] T037 [US2] Add resources endpoint in C:/Users/akhil/behaviour_lab/app/api/routes/resources.py (Depends on: T010,T031; Output: `GET /scenarios/{id}/resources`)
- [X] T038 [US2] Extend timeline filtering with zone-aware event visibility in C:/Users/akhil/behaviour_lab/app/api/routes/timeline.py (Depends on: T035,T036,T037; Output: timeline queries filterable by zone/event class)
- [X] T039 [US2] Add zones dashboard page with occupancy view in C:/Users/akhil/behaviour_lab/app/dashboard/pages/zones.py (Depends on: T036; Output: visual zone occupancy and opportunities page)
- [X] T040 [US2] Add resources dashboard page with quantity/status tracking in C:/Users/akhil/behaviour_lab/app/dashboard/pages/resources.py (Depends on: T037; Output: visual resource availability page)
- [X] T041 [US2] Extend timeline dashboard to show plan/resource/zone effects in C:/Users/akhil/behaviour_lab/app/dashboard/pages/timeline.py (Depends on: T038; Output: causal Phase 3 timeline inspection)
- [X] T042 [US2] Register zones/resources page access in C:/Users/akhil/behaviour_lab/app/dashboard/main.py (Depends on: T039,T040; Output: navigable world-state pages)
- [X] T043 [US2] Update story-level run steps for zones/resources/interruption inspection in C:/Users/akhil/behaviour_lab/specs/001-behavior-lab-simulation/quickstart.md (Depends on: T039,T040,T041; Output: executable US2 validation steps)

**Checkpoint**: User Stories 1 and 2 are fully functional and independently testable.

---

## Phase 5: User Story 3 - Compare Goal-Directed Behavioral Variants (Priority: P3)

**Goal**: Researchers can compare how changes to needs, goals, resource layout, or starting zone context alter deterministic behavior and plan outcomes.

**Independent Test**: Re-run the same scenario with one changed need threshold or resource/starting-location parameter and verify the comparison output shows at least three observable differences in plan transitions, movement/resource events, or social outcomes.

### Tests for User Story 3

- [X] T044 [P] [US3] Add scenario test for goal/resource variant comparison in C:/Users/akhil/behaviour_lab/tests/scenario/test_goal_resource_variant_diff.py (Depends on: T012,T035; Output: stable difference assertions for situated variants)
- [X] T045 [P] [US3] Add integration test for compare-rerun with planning/world overrides in C:/Users/akhil/behaviour_lab/tests/integration/test_planning_variant_compare.py (Depends on: T012; Output: deterministic compare-rerun support for Phase 3 state)

### Implementation for User Story 3

- [X] T046 [US3] Extend scenario variant loader for need/resource/location overrides in C:/Users/akhil/behaviour_lab/app/simulation/scenario_loader.py (Depends on: T031,T032; Output: cloneable Phase 3 world/planning variants)
- [X] T047 [US3] Extend compare-rerun API to include planning/resource/location differences in C:/Users/akhil/behaviour_lab/app/api/routes/simulation.py (Depends on: T046; Output: richer comparison summary for Phase 3)
- [X] T048 [US3] Persist planning/resource comparison metadata in C:/Users/akhil/behaviour_lab/app/persistence/models.py (Depends on: T046,T047; Output: auditable comparison records for Phase 3 metrics)
- [X] T049 [US3] Extend comparison dashboard page for plan/resource/location deltas in C:/Users/akhil/behaviour_lab/app/dashboard/pages/comparison.py (Depends on: T047; Output: visible Phase 3 comparison interface)
- [X] T050 [US3] Update comparison run walkthrough for Phase 3 variants in C:/Users/akhil/behaviour_lab/specs/001-behavior-lab-simulation/quickstart.md (Depends on: T049; Output: executable US3 validation steps)

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that strengthen demo clarity, reproducibility, and Phase 3 observability.

- [X] T051 [P] Add Phase 3 end-to-end smoke test in C:/Users/akhil/behaviour_lab/tests/smoke/test_phase3_goal_resource_flow.py (Depends on: T043; Output: full needs-goals-zones-resources-planning smoke coverage)
- [X] T052 [P] Refine runner/tick trace labels for planning and world actions in C:/Users/akhil/behaviour_lab/app/simulation/runner.py (Depends on: T035; Output: clearer lifecycle diagnostics for Phase 3)
- [X] T053 Document Phase 3 MVP run sequence and extension limits in C:/Users/akhil/behaviour_lab/README.md (Depends on: T050; Output: practical local demo guide for Phase 3)
- [X] T054 Add Phase 3 demo troubleshooting guide in C:/Users/akhil/behaviour_lab/docs/phase3-demo.md (Depends on: T053; Output: operator-oriented demo/debug checklist)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: can start immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: depends on foundational planning/world persistence.
- **Phase 4 (US2)**: depends on US1 planning state and foundational world repositories.
- **Phase 5 (US3)**: depends on US1 + US2 planning/resource/zone features.
- **Phase 6 (Polish)**: depends on target user stories being complete.

### User Story Dependency Graph

- **US1 (P1)** -> **US2 (P2)** -> **US3 (P3)**

### Parallel Opportunities by Story

- **US1**: T013, T014, and T015 can run in parallel; T024 and T025 can run in parallel after T021.
- **US2**: T028, T029, and T030 can run in parallel; T039 and T040 can run in parallel after T036/T037.
- **US3**: T044 and T045 can run in parallel; T048 and T049 can run in parallel after T047.

## Parallel Execution Examples

### US1

```bash
Task: "Add contract test for goals/intentions endpoints in tests/contract/test_goals_contract.py"
Task: "Add integration test for goal/intention persistence and transitions in tests/integration/test_goal_intention_persistence.py"
Task: "Add scenario test for deterministic need-driven action divergence in tests/scenario/test_need_driven_planning.py"
```

### US2

```bash
Task: "Add contract test for zones/resources endpoints in tests/contract/test_world_contract.py"
Task: "Add integration test for resource acquire/consume/shortage cases in tests/integration/test_resource_flow.py"
Task: "Add scenario test for interruption and replanning flow in tests/scenario/test_interruption_replanning.py"
```

### US3

```bash
Task: "Add scenario test for goal/resource variant comparison in tests/scenario/test_goal_resource_variant_diff.py"
Task: "Add integration test for compare-rerun with planning/world overrides in tests/integration/test_planning_variant_compare.py"
```

---

## Critical Path (Minimum Phase 3 MVP)

1. T001 -> T002 -> T003 -> T004 -> T005
2. T006 -> T007 -> T008 -> T009 -> T010 -> T011 -> T012
3. T016 -> T017 -> T018 -> T020 -> T022 -> T023
4. T031 -> T032 -> T033 -> T034 -> T035
5. T021 -> T024 -> T025 -> T026
6. T036 -> T037 -> T038 -> T039 -> T040 -> T041 -> T042 -> T043
7. T051 -> T053

This path yields a working Phase 3 MVP with explicit goals, needs, zone/resource grounding,
deterministic replanning, and dashboard-observable state transitions.

## Defer for Later (Do Not Build in Phase 3 MVP)

- Full LLM freeform planning
- Vector memory infrastructure
- Websockets
- Authentication/authorization
- Cloud deployment infrastructure
- Distributed-agent orchestration
- Pygame / 2D embodiment
- Full physics or movement engine
- Complex economy system
- Complex emotion engine

---

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Deliver US1 and validate goal/intention persistence with need-driven decisions.
3. Deliver US2 and validate zone/resource/interruption visibility.
4. Stop for Phase 3 MVP demo before expanding variant comparison depth.

### Incremental Delivery

1. US1: goals, intentions, and needs.
2. US2: zones, resources, movement, and interruptions.
3. US3: comparison support for planning/world variants.
4. Polish: smoke coverage, docs, and demo guidance.

### Validation Rule

Every completed task must preserve deterministic replay, persisted observability, and local-first execution.
