# Tasks: Phase 2 Social Dynamics for Multi-Agent Behavior Lab

**Input**: Design documents from `C:/Users/akhil/behaviour_lab/specs/001-behavior-lab-simulation/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Test tasks are included because spec acceptance depends on deterministic behavior, persisted traceability, and social observability.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Parallelizable task (different files, no unmet dependency)
- **[Story]**: Appears only in user-story phases (`[US1]`, `[US2]`, `[US3]`)

## Phase 1: Setup (Phase 2 Baseline)

**Purpose**: Prepare Phase 2 social-dynamics implementation surface on top of completed Phase 1 scaffold.

- [X] T001 Align Phase 2 dependency set and dev extras in C:/Users/akhil/behaviour_lab/pyproject.toml (Output: reproducible local dependency graph)
- [X] T002 Add deterministic social-sim settings in C:/Users/akhil/behaviour_lab/app/schemas/settings.py (Output: config flags for persona/relationship/event behavior)
- [X] T003 [P] Update local environment defaults for Phase 2 in C:/Users/akhil/behaviour_lab/.env.example (Output: runnable local-first defaults)
- [X] T004 [P] Add Phase 2 scenario config seed input in C:/Users/akhil/behaviour_lab/app/configs/scenarios/sample_social_tension.yaml (Output: reusable social tension scenario)
- [X] T005 [P] Add shared social enums/contracts in C:/Users/akhil/behaviour_lab/app/schemas/social.py (Output: single source for action/intent/tone/event types)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema and service scaffolding that must be finished before user-story slices.

**CRITICAL**: User-story implementation begins only after this phase is complete.

- [X] T006 Extend persisted social entities and fields in C:/Users/akhil/behaviour_lab/app/persistence/models.py (Depends on: T001; Output: Message/Relationship/SimulationEvent/DecisionLog Phase 2 fields)
- [X] T007 Apply constraints and indexes for social queries in C:/Users/akhil/behaviour_lab/app/persistence/init_db.py (Depends on: T006; Output: deterministic DB integrity and query performance)
- [X] T008 [P] Add message/relationship/event repository primitives in C:/Users/akhil/behaviour_lab/app/persistence/repositories/social_repository.py (Depends on: T006; Output: reusable persistence API)
- [X] T009 [P] Create communication service scaffold in C:/Users/akhil/behaviour_lab/app/communication/handlers.py (Depends on: T005; Output: injectable message orchestration entrypoints)
- [X] T010 [P] Create relationship policy scaffold in C:/Users/akhil/behaviour_lab/app/agents/relationship_policy.py (Depends on: T005; Output: deterministic relationship update policy contract)
- [X] T011 [P] Add scenario event injection scaffold in C:/Users/akhil/behaviour_lab/app/simulation/world_state.py (Depends on: T005; Output: scheduled world-event ingestion surface)
- [X] T012 Add API social schemas for requests/responses in C:/Users/akhil/behaviour_lab/app/api/schemas/social.py (Depends on: T005; Output: typed API payload models)
- [X] T013 Add integration fixture for seeded triad scenarios in C:/Users/akhil/behaviour_lab/tests/integration/conftest.py (Depends on: T004,T007; Output: shared deterministic test harness)

**Checkpoint**: Foundation complete; US1/US2/US3 work can proceed.

---

## Phase 3: User Story 1 - Run a Small Social Scenario (Priority: P1) MVP

**Goal**: Enable deterministic multi-agent communication and persona/world-aware social actions in the tick loop.

**Independent Test**: Run a 3-agent scenario for 10 ticks and verify persisted decisions/messages show distinct persona-driven behavior.

### Tests for User Story 1

- [X] T014 [P] [US1] Add message API contract test in C:/Users/akhil/behaviour_lab/tests/contract/test_messages_contract.py (Depends on: T012; Output: locked message query contract)
- [X] T015 [P] [US1] Add integration test for message persistence from ticks in C:/Users/akhil/behaviour_lab/tests/integration/test_message_persistence.py (Depends on: T013; Output: verified sender/receiver/intent/tone/tick persistence)
- [X] T016 [P] [US1] Add scenario test for deterministic persona action divergence in C:/Users/akhil/behaviour_lab/tests/scenario/test_persona_determinism.py (Depends on: T013; Output: reproducible differential behavior evidence)

### Implementation for User Story 1

- [X] T017 [US1] Implement message create/query repository methods in C:/Users/akhil/behaviour_lab/app/persistence/repositories/social_repository.py (Depends on: T008; Output: persisted message read/write operations)
- [X] T018 [US1] Implement structured message creation flow in C:/Users/akhil/behaviour_lab/app/communication/message_bus.py (Depends on: T009,T017; Output: tick-driven Message records with intent and tone)
- [X] T019 [US1] Emit message SimulationEvents with causal IDs in C:/Users/akhil/behaviour_lab/app/communication/handlers.py (Depends on: T018; Output: message events linked to decisions)
- [X] T020 [US1] Add message query endpoint with filters in C:/Users/akhil/behaviour_lab/app/api/routes/scenarios.py (Depends on: T012,T017; Output: `GET /scenarios/{id}/messages` with scenario/agent/tick filters)
- [X] T021 [US1] Extend persona trait fields and normalization in C:/Users/akhil/behaviour_lab/app/agents/models.py (Depends on: T005; Output: explicit cooperation/risk/style/sensitivity fields)
- [X] T022 [US1] Apply persona decision and tone bias logic in C:/Users/akhil/behaviour_lab/app/agents/decision_policy.py (Depends on: T021; Output: deterministic persona-weighted action selection)
- [X] T023 [US1] Implement scenario event injection loading in C:/Users/akhil/behaviour_lab/app/simulation/world_state.py (Depends on: T011; Output: per-tick world-event inputs)
- [X] T024 [US1] Persist world_event SimulationEvents in C:/Users/akhil/behaviour_lab/app/simulation/runner.py (Depends on: T023; Output: world events visible in timeline data)
- [X] T025 [US1] Upgrade tick action routing (warn/cooperate/avoid/propose/observe/wait) in C:/Users/akhil/behaviour_lab/app/simulation/tick_engine.py (Depends on: T018,T022,T023; Output: deterministic social action execution)
- [X] T026 [US1] Persist decision rationale context fields in C:/Users/akhil/behaviour_lab/app/simulation/tick_engine.py (Depends on: T025; Output: traceable decision logs with persona/world factors)
- [X] T027 [US1] Link message outcomes to memory writes and recall traces in C:/Users/akhil/behaviour_lab/app/memory/writer.py (Depends on: T019,T026; Output: memory records tied to social interactions)
- [X] T028 [US1] Add seeded message-intent examples in C:/Users/akhil/behaviour_lab/app/persistence/seed.py (Depends on: T004,T021; Output: deterministic sample communication patterns)
- [X] T029 [US1] Add communication feed page in C:/Users/akhil/behaviour_lab/app/dashboard/pages/communication.py (Depends on: T020; Output: message feed UI from persisted state)
- [X] T030 [US1] Register communication page routing in C:/Users/akhil/behaviour_lab/app/dashboard/main.py (Depends on: T029; Output: navigable communication view)
- [X] T031 [US1] Update US1 run/demo instructions in C:/Users/akhil/behaviour_lab/specs/001-behavior-lab-simulation/quickstart.md (Depends on: T020,T025; Output: executable local demo for US1)

**Checkpoint**: US1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Inspect Memory and Social Effects (Priority: P2)

**Goal**: Make relationship evolution and memory-social causality inspectable through API and dashboard.

**Independent Test**: Run a scenario where two agents interact twice with an intermediate event; verify relationship deltas and memory traces explain the changed second interaction.

### Tests for User Story 2

- [X] T032 [P] [US2] Add relationship API contract test in C:/Users/akhil/behaviour_lab/tests/contract/test_relationships_contract.py (Depends on: T012; Output: locked relationship query contract)
- [X] T033 [P] [US2] Add integration test for trust/affinity updates in C:/Users/akhil/behaviour_lab/tests/integration/test_relationship_updates.py (Depends on: T013; Output: validated interaction-driven relationship changes)
- [X] T034 [P] [US2] Add integration test for social causal chain fields in C:/Users/akhil/behaviour_lab/tests/integration/test_social_trace_chain.py (Depends on: T013,T026; Output: verified memory->decision->message->relationship traceability)

### Implementation for User Story 2

- [X] T035 [US2] Implement deterministic relationship update rules in C:/Users/akhil/behaviour_lab/app/agents/relationship_policy.py (Depends on: T010,T022; Output: repeatable trust/affinity deltas by interaction intent/tone)
- [X] T036 [US2] Persist relationship updates and timestamps in C:/Users/akhil/behaviour_lab/app/persistence/repositories/social_repository.py (Depends on: T035,T008; Output: durable Relationship history)
- [X] T037 [US2] Emit relationship_update events with causal payloads in C:/Users/akhil/behaviour_lab/app/simulation/tick_engine.py (Depends on: T036; Output: timeline-visible relationship transitions)
- [X] T038 [US2] Add relationship query endpoint and filters in C:/Users/akhil/behaviour_lab/app/api/routes/relationships.py (Depends on: T032,T036; Output: `GET /scenarios/{id}/relationships`)
- [X] T039 [US2] Extend timeline filtering by social event types in C:/Users/akhil/behaviour_lab/app/api/routes/timeline.py (Depends on: T037; Output: filtered timeline queries by event_type/agent/tick)
- [X] T040 [US2] Implement relationship state dashboard table view in C:/Users/akhil/behaviour_lab/app/dashboard/pages/relationships.py (Depends on: T038; Output: inspectable relationship matrix/history)
- [X] T041 [US2] Improve agent detail social context panel in C:/Users/akhil/behaviour_lab/app/dashboard/pages/agents.py (Depends on: T039,T040; Output: persona + messages + relationships + recalled memories in one view)
- [X] T042 [US2] Improve timeline page for social event rendering in C:/Users/akhil/behaviour_lab/app/dashboard/pages/timeline.py (Depends on: T039; Output: explicit message/relationship/world event entries)
- [X] T043 [US2] Add reusable dashboard social filters in C:/Users/akhil/behaviour_lab/app/dashboard/components/filters.py (Depends on: T039; Output: scenario/agent/tick/event-type filters)
- [X] T044 [US2] Enforce persisted-state reads in dashboard client in C:/Users/akhil/behaviour_lab/app/dashboard/components/api_client.py (Depends on: T040,T042; Output: no in-memory-only fallback paths)
- [X] T045 [US2] Extend seeded relationship progression data in C:/Users/akhil/behaviour_lab/app/persistence/seed.py (Depends on: T035; Output: realistic social trajectory for demos/tests)
- [X] T046 [US2] Update US2 inspection walkthrough in C:/Users/akhil/behaviour_lab/specs/001-behavior-lab-simulation/quickstart.md (Depends on: T041,T042; Output: repeatable social-effect inspection steps)

**Checkpoint**: US2 is fully functional and independently testable.

---

## Phase 5: User Story 3 - Compare Behavioral Variants (Priority: P3)

**Goal**: Support controlled reruns with persona/context changes and visible comparative outcomes.

**Independent Test**: Re-run the same scenario with one persona variable changed and verify at least three observable differences in decisions/messages/relationship trends.

### Tests for User Story 3

- [X] T047 [P] [US3] Add scenario test for persona variant comparison in C:/Users/akhil/behaviour_lab/tests/scenario/test_run_variant_comparison.py (Depends on: T013,T045; Output: stable run-diff assertions)
- [X] T048 [P] [US3] Add integration test for reset and rerun consistency in C:/Users/akhil/behaviour_lab/tests/integration/test_scenario_rerun_consistency.py (Depends on: T013; Output: deterministic rerun behavior)

### Implementation for User Story 3

- [X] T049 [US3] Implement rerun-with-overrides loader flow in C:/Users/akhil/behaviour_lab/app/simulation/scenario_loader.py (Depends on: T023,T045; Output: scenario variants with persona/start-context deltas)
- [X] T050 [US3] Add compare/rerun simulation endpoint in C:/Users/akhil/behaviour_lab/app/api/routes/simulation.py (Depends on: T049; Output: controllable variant run API)
- [X] T051 [US3] Add comparison dashboard page for run deltas in C:/Users/akhil/behaviour_lab/app/dashboard/pages/comparison.py (Depends on: T050; Output: visible differences across runs)
- [X] T052 [US3] Register comparison page navigation in C:/Users/akhil/behaviour_lab/app/dashboard/main.py (Depends on: T051; Output: accessible comparison UX)
- [X] T053 [US3] Persist run metadata and comparison summary events in C:/Users/akhil/behaviour_lab/app/persistence/models.py (Depends on: T049; Output: auditable run-variant metadata)
- [X] T054 [US3] Update US3 comparison demo in C:/Users/akhil/behaviour_lab/specs/001-behavior-lab-simulation/quickstart.md (Depends on: T051,T053; Output: executable comparison workflow)

**Checkpoint**: US3 is fully functional and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening for Phase 2 MVP usability and clarity.

- [ ] T055 [P] Add Phase 2 end-to-end smoke test in C:/Users/akhil/behaviour_lab/tests/smoke/test_phase2_social_flow.py (Depends on: T046; Output: full social-loop smoke coverage)
- [ ] T056 [P] Improve structured event/decision logging labels in C:/Users/akhil/behaviour_lab/app/simulation/runner.py (Depends on: T026,T037; Output: clearer timeline diagnostics)
- [ ] T057 Document Phase 2 MVP run sequence and limitations in C:/Users/akhil/behaviour_lab/README.md (Depends on: T054; Output: practical local demo guide)
- [ ] T058 Add Phase 2 demo troubleshooting guide in C:/Users/akhil/behaviour_lab/docs/phase2-demo.md (Depends on: T057; Output: operator-oriented debug checklist)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: start immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all stories.
- **Phase 3 (US1)**: starts after foundational completion.
- **Phase 4 (US2)**: depends on US1 social artifacts and foundational services.
- **Phase 5 (US3)**: depends on US1 + US2 data and APIs.
- **Phase 6 (Polish)**: depends on target user stories being complete.

### User Story Dependency Graph

- **US1 (P1)** -> **US2 (P2)** -> **US3 (P3)**

### Parallel Opportunities by Story

- **US1**: T014, T015, T016 can run in parallel; T021 and T023 can run in parallel after T005/T011.
- **US2**: T032, T033, T034 can run in parallel; T040 and T042 can run in parallel after T039.
- **US3**: T047 and T048 can run in parallel; T051 and T053 can run in parallel after T050/T049 respectively.

## Parallel Execution Examples

### US1

```bash
# Parallel test authoring
T014 + T015 + T016

# Parallel implementation after foundations
T021 + T023
```

### US2

```bash
# Parallel validation tasks
T032 + T033 + T034

# Parallel dashboard work once API filters exist
T040 + T042
```

### US3

```bash
# Parallel tests
T047 + T048

# Parallel persistence/UI prep
T051 + T053
```

---

## Critical Path (Minimum Phase 2 MVP)

1. T001 -> T002 -> T005 -> T006 -> T007 -> T008 -> T009 -> T011 -> T012 -> T013
2. T017 -> T018 -> T019 -> T021 -> T022 -> T023 -> T024 -> T025 -> T026 -> T027
3. T020 -> T029 -> T030 -> T031
4. T035 -> T036 -> T037 -> T038 -> T039 -> T040 -> T041 -> T042 -> T046
5. T055 -> T057

This path yields a working MVP with social messaging, relationship updates, persona/world influence, and inspectable dashboard flows.

## Defer for Later (Do Not Build in Phase 2 MVP)

- LLM-driven freeform planning
- Vector-memory infrastructure
- Websockets
- Authentication/authorization
- Cloud deployment infrastructure
- Distributed-agent orchestration
- 2D movement or game-world embodiment
- Microservices split
- Complex emotion-engine modeling

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Deliver US1 and verify independent test criteria.
3. Add US2 for social-effect inspection and traceability.
4. Stop for MVP demo before US3 comparison expansion.

### Incremental Delivery

1. US1: communication + deterministic persona/world-aware actions.
2. US2: relationship and observability depth.
3. US3: controlled comparison workflows.
4. Polish: smoke tests, docs, and operator guidance.

### Validation Rule

Every completed task must preserve persisted-state observability and local deterministic reproducibility.
