# Tasks: Phase 4 Hybrid Decision Engine

**Input**: Design documents from `/specs/001-behavior-observatory/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for story structure), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required for this phase. Execute unit, integration, scenario, contract, and smoke coverage for deterministic/llm/hybrid routing and fallback safety.

**Organization**: Tasks are grouped by user story and mapped to the requested Phase 4 slices. Scope is limited to hybrid decision-engine integration, observability, comparison, and docs.

## Format: `[ID] [P?] [Story?] Description with file path`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold Phase 4 files and configuration surfaces before core behavior changes.

- [X] T001 Create decision-engine module scaffold in app/agents/decision_engine.py [Deps: none] [Output: DecisionEngine interface and mode enum placeholders]
- [X] T002 [P] Create llm policy scaffold in app/agents/llm_policy.py [Deps: none] [Output: LlmPolicy interface placeholder with typed request/response signatures]
- [X] T003 [P] Create prompt builder and parser scaffolds in app/agents/prompt_builder.py and app/agents/response_parser.py [Deps: none] [Output: Prompt builder/parser module placeholders]
- [X] T004 [P] Create model adapter scaffold in app/agents/model_adapter.py [Deps: none] [Output: provider-agnostic adapter interface placeholder]
- [X] T005 Create structured decision schema scaffold in app/schemas/decision_engine.py [Deps: none] [Output: shared structured decision Pydantic models]
- [X] T006 Add Phase 4 test skeleton files in tests/unit/test_decision_engine.py, tests/unit/test_prompt_builder.py, tests/unit/test_response_parser.py [Deps: none] [Output: empty test modules ready for TDD]

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the mandatory contracts and persistence/config plumbing required before policy integration.

**CRITICAL**: No user story implementation should complete until this phase is done.

- [X] T007 Extend policy mode and llm config settings in app/schemas/settings.py [Deps: T005] [Output: global defaults for deterministic/llm/hybrid, timeout, model config]
- [X] T008 [P] Extend run request/response schemas for policy overrides in app/schemas/api.py [Deps: T005] [Output: API contract supports policy_mode and llm_config]
- [X] T009 Update run endpoint request handling in app/api/routes/simulation.py [Deps: T008] [Output: run API accepts and forwards policy overrides]
- [X] T010 Add run-level metadata support for policy settings in app/persistence/models.py [Deps: T008] [Output: RunMetadata stores policy mode/provider/model/overrides]
- [X] T011 [P] Add decision metadata fields for source/parser/fallback in app/persistence/models.py [Deps: T005] [Output: DecisionLog includes decision_source, parser_status, fallback_reason, prompt metadata]
- [X] T012 Update DB init/seed compatibility for new metadata fields in app/persistence/init_db.py and app/persistence/seed.py [Deps: T010, T011] [Output: local DB initializes cleanly with new columns]
- [X] T013 Create run metadata repository helpers in app/persistence/repositories/run_repository.py [Deps: T010] [Output: save/load helpers for policy-mode run metadata]
- [X] T014 Add shared allowed action/intent/tone contract constants in app/schemas/social.py and app/schemas/decision_engine.py [Deps: T005] [Output: canonical allowlist used by deterministic and llm validation]
- [X] T015 Define fallback reason/status taxonomy in app/schemas/decision_engine.py [Deps: T005] [Output: standardized parser/fallback reason enums]
- [X] T016 Update Phase 4 contracts in specs/001-behavior-observatory/contracts/api.openapi.yaml and specs/001-behavior-observatory/contracts/decision-engine-contract.md [Deps: T009, T014, T015] [Output: contracts reflect policy mode, fallback, and observability fields]

**Checkpoint**: Foundation complete; user story implementation can proceed safely.

---

## Phase 3: User Story 1 - Safe Hybrid Decision Execution (Priority: P1)

**Goal**: Route each tick through a mode-aware decision engine (`deterministic`, `llm`, `hybrid`) with strict structured-output parsing and deterministic fallback.

**Independent Test**: A seeded scenario runs in all three modes; invalid/timeout llm outputs fall back to deterministic within the same tick without breaking downstream execution.

### Tests for User Story 1

- [X] T017 [P] [US1] Add routing unit tests in tests/unit/test_decision_engine.py [Deps: T001, T005] [Output: deterministic/llm/hybrid route assertions]
- [X] T018 [P] [US1] Add prompt-context assembly unit tests in tests/unit/test_prompt_builder.py [Deps: T003] [Output: context includes persona/needs/goal/intention/zone/resources/events/relationships/memory]
- [X] T019 [P] [US1] Add parser contract unit tests in tests/unit/test_response_parser.py [Deps: T003, T015] [Output: valid, invalid-json, schema-fail, and constraint-fail cases]
- [X] T020 [P] [US1] Add fallback integration test in tests/integration/test_llm_fallback.py [Deps: T002, T003, T004] [Output: deterministic fallback on timeout/provider/parse failures]
- [X] T021 [P] [US1] Add policy-mode integration test in tests/integration/test_policy_mode_routing.py [Deps: T009, T017] [Output: run endpoint selects requested policy mode]
- [X] T022 [P] [US1] Add simulation policy contract test in tests/contract/test_simulation_policy_contract.py [Deps: T008, T009, T016] [Output: API schema and response fields validated]

### Implementation for User Story 1

- [X] T023 [US1] Implement DecisionEngine interface and mode routing in app/agents/decision_engine.py [Deps: T017, T014, T015] [Output: unified resolver with deterministic/llm/hybrid branches]
- [X] T024 [US1] Refactor deterministic policy adapter to structured-decision output in app/agents/decision_policy.py [Deps: T023] [Output: deterministic path returns shared StructuredDecision model]
- [X] T025 [US1] Implement prompt/context builder with bounded summaries in app/agents/prompt_builder.py [Deps: T018, T014] [Output: deterministic truncation and ordered context blocks]
- [X] T026 [US1] Implement model adapter base and first provider client in app/agents/model_adapter.py [Deps: T004, T007] [Output: timeout-aware provider call abstraction]
- [X] T027 [US1] Implement llm policy using prompt builder and adapter in app/agents/llm_policy.py [Deps: T025, T026] [Output: raw response acquisition with latency metadata]
- [X] T028 [US1] Implement structured response parser and schema validator in app/agents/response_parser.py [Deps: T019, T014, T015] [Output: parsed decision result with explicit status]
- [X] T029 [US1] Implement world-constraint validation hook for parsed decisions in app/agents/response_parser.py [Deps: T028] [Output: illegal action/target detection before execution]
- [X] T030 [US1] Implement deterministic fallback orchestration in app/agents/decision_engine.py [Deps: T020, T024, T027, T029] [Output: fallback path with reason/status propagation]
- [X] T031 [US1] Replace direct policy call with decision engine in app/simulation/tick_engine.py [Deps: T023, T030] [Output: tick flow uses decision engine output only]
- [X] T032 [US1] Thread policy mode and llm config from runner into tick execution in app/simulation/runner.py [Deps: T009, T013, T031] [Output: per-run policy mode selection active]
- [X] T033 [US1] Preserve downstream message/relationship/memory flow compatibility in app/simulation/tick_engine.py [Deps: T031] [Output: existing world execution path unchanged after decision selection]
- [X] T034 [US1] Persist decision source/parser/fallback metadata in app/simulation/tick_engine.py and app/persistence/models.py [Deps: T011, T031] [Output: DecisionLog rows include Phase 4 metadata]
- [X] T035 [US1] Emit fallback and parse-failure events in app/simulation/tick_engine.py [Deps: T015, T034] [Output: timeline includes llm_parse_error and llm_fallback events]

**Checkpoint**: Hybrid decision execution is functional and safe with deterministic fallback.

---

## Phase 4: User Story 2 - Observability and Comparison for Policy Modes (Priority: P2)

**Goal**: Make deterministic vs llm/hybrid behavior fully inspectable and comparable in persisted analytics and rerun workflows.

**Independent Test**: Two runs of the same scenario in different policy modes can be compared with visible source distribution, fallback rate, and behavior deltas.

### Tests for User Story 2

- [X] T036 [P] [US2] Add comparison integration tests for policy metadata and fallback counts in tests/integration/test_policy_mode_comparison.py [Deps: T013, T034] [Output: deterministic vs llm/hybrid comparison assertions]
- [X] T037 [P] [US2] Add analytics integration tests for decision-source filters in tests/integration/test_phase4_observability.py [Deps: T034, T035] [Output: API returns source/fallback fields and filter behavior]
- [X] T038 [P] [US2] Add scenario rerun comparison test in tests/scenario/test_phase4_policy_compare.py [Deps: T032, T036] [Output: scenario variant comparison flow validated]
- [X] T039 [P] [US2] Add contract test for comparison payload policy fields in tests/contract/test_policy_comparison_contract.py [Deps: T016, T036] [Output: comparison API contract validation]
- [X] T040 [P] [US2] Add dashboard data contract test for decision-source visibility in tests/contract/test_agent_observability_contract.py [Deps: T037] [Output: observability payload includes source/parser/fallback metadata]

### Implementation for User Story 2

- [X] T041 [US2] Extend comparison metrics aggregation for policy-mode diffs in app/analytics/comparison_analytics.py [Deps: T036] [Output: action/fallback/cooperation/conflict/goal deltas by mode]
- [X] T042 [US2] Update compare endpoint with policy metadata in app/api/routes/scenarios.py [Deps: T041, T039] [Output: compare response includes policy mode and fallback statistics]
- [X] T043 [US2] Expose decision-source and fallback fields in agent analytics payloads in app/analytics/agent_analytics.py [Deps: T034, T037] [Output: observability APIs include source/parser/fallback details]
- [X] T044 [US2] Add decision-source filter support in analytics routes in app/api/routes/analytics_agents.py and app/api/routes/timeline.py [Deps: T043] [Output: filterable observability by decision source]
- [X] T045 [US2] Surface policy-mode metadata in run outputs in app/api/routes/simulation.py [Deps: T032, T042] [Output: run API returns policy mode and fallback counts]
- [X] T046 [US2] Update comparison dashboard view for policy-mode deltas in app/dashboard/pages/comparison.py [Deps: T041, T042] [Output: UI shows deterministic vs llm/hybrid diff panels]
- [X] T047 [US2] Update agent intelligence page to show decision source and fallback badges in app/dashboard/pages/agent_intelligence.py [Deps: T043, T044] [Output: per-decision source/fallback visibility]
- [X] T048 [US2] Persist llm config summary for reruns in app/persistence/repositories/run_repository.py and app/simulation/runner.py [Deps: T013, T032] [Output: run metadata captures llm config needed for replay]

**Checkpoint**: Policy-mode observability and comparison are operational.

---

## Phase 5: User Story 3 - Validation, Runbooks, and Safe Adoption (Priority: P3)

**Goal**: Provide reproducible test coverage, smoke safety, and operator documentation for Phase 4 usage.

**Independent Test**: A developer can run documented deterministic/llm/hybrid workflows, reproduce fallback behavior, and validate outputs using automated tests and runbooks.

### Tests for User Story 3

- [X] T049 [P] [US3] Add end-to-end tick integration test for hybrid mode in tests/integration/test_tick_engine_hybrid_integration.py [Deps: T031, T033, T034] [Output: full tick pipeline remains stable]
- [X] T050 [P] [US3] Add fallback reproducibility scenario test in tests/scenario/test_phase4_fallback_repro.py [Deps: T030, T035] [Output: deterministic rescue path repeatability]
- [X] T051 [P] [US3] Add llm-enabled smoke test with forced fallback branch in tests/smoke/test_phase4_hybrid_flow.py [Deps: T049, T050] [Output: smoke coverage for success + fallback path]
- [X] T052 [P] [US3] Add prompt-size guardrail unit tests in tests/unit/test_prompt_budgeting.py [Deps: T025] [Output: truncation rules and token-budget safeguards]
- [X] T053 [P] [US3] Add parser legality regression tests in tests/unit/test_response_legality.py [Deps: T029] [Output: impossible actions always rejected pre-execution]

### Implementation for User Story 3

- [X] T054 [US3] Update README with Phase 4 policy-mode usage in README.md [Deps: T045, T051] [Output: deterministic/llm/hybrid run commands documented]
- [X] T055 [US3] Add Phase 4 runbook and fallback troubleshooting guide in docs/phase4-hybrid-runbook.md [Deps: T051] [Output: operator workflow for fallback diagnosis]
- [X] T056 [US3] Document comparison workflow for policy modes in specs/001-behavior-observatory/quickstart.md [Deps: T046, T051] [Output: deterministic vs llm/hybrid evaluation steps]
- [X] T057 [US3] Document prompt/response observability limitations in specs/001-behavior-observatory/contracts/dashboard-data-contract.md [Deps: T043, T055] [Output: clear metadata retention and debug-mode boundaries]
- [X] T058 [US3] Update implementation plan notes for delivered Phase 4 scope in specs/001-behavior-observatory/plan.md [Deps: T054, T056, T057] [Output: plan reflects completed architecture decisions and guardrails]

**Checkpoint**: Phase 4 is validated, documented, and safely operable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening and consistency checks across all stories.

- [ ] T059 [P] Run and fix full test suite regressions for Phase 4 in tests/ [Deps: T049, T050, T051, T052, T053] [Output: all tests pass with new policy modes]
- [ ] T060 Verify structured decision schema parity across deterministic and llm paths in app/agents/decision_policy.py and app/agents/llm_policy.py [Deps: T024, T027, T028] [Output: no schema drift between policy implementations]
- [ ] T061 [P] Finalize API/contract examples for policy mode and fallback metadata in specs/001-behavior-observatory/contracts/api.openapi.yaml [Deps: T042, T045] [Output: examples aligned with shipped API behavior]
- [ ] T062 Mark completed tasks and record Phase 4 completion notes in specs/001-behavior-observatory/tasks.md and docs/phase4-hybrid-runbook.md [Deps: T059, T060, T061] [Output: accurate execution tracking and closure notes]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: start immediately.
- **Foundational (Phase 2)**: depends on setup; blocks all user stories.
- **US1 (Phase 3)**: depends on foundational completion.
- **US2 (Phase 4)**: depends on US1 decision metadata and routing outputs.
- **US3 (Phase 5)**: depends on US1 + US2 features.
- **Polish (Phase 6)**: depends on all stories.

### User Story Dependency Graph

- **US1 (P1)** -> **US2 (P2)** -> **US3 (P3)**

### Within Each User Story

- tests first (contract/integration/scenario/unit)
- engine/schema updates before tick integration
- persistence/observability before dashboard/comparison surfaces
- documentation after tested behavior is stable

### Parallel Opportunities

- Foundational tasks marked `[P]` can run in parallel after schema decisions.
- US1 tests `T017-T022` can run in parallel.
- US2 tests `T036-T040` can run in parallel.
- US3 tests `T049-T053` can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "Add routing unit tests in tests/unit/test_decision_engine.py"
Task: "Add prompt-context assembly unit tests in tests/unit/test_prompt_builder.py"
Task: "Add parser contract unit tests in tests/unit/test_response_parser.py"
Task: "Add fallback integration test in tests/integration/test_llm_fallback.py"
Task: "Add policy-mode integration test in tests/integration/test_policy_mode_routing.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add comparison integration tests in tests/integration/test_policy_mode_comparison.py"
Task: "Add analytics integration tests in tests/integration/test_phase4_observability.py"
Task: "Add scenario rerun comparison test in tests/scenario/test_phase4_policy_compare.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add end-to-end tick integration test in tests/integration/test_tick_engine_hybrid_integration.py"
Task: "Add fallback reproducibility scenario test in tests/scenario/test_phase4_fallback_repro.py"
Task: "Add llm-enabled smoke test in tests/smoke/test_phase4_hybrid_flow.py"
```

---

## Critical Path

1. `T005` -> `T007` -> `T008` -> `T009` -> `T010` -> `T011` -> `T012`
2. `T023` -> `T024` -> `T025` -> `T026` -> `T027` -> `T028` -> `T029` -> `T030`
3. `T031` -> `T032` -> `T033` -> `T034` -> `T035`
4. `T041` -> `T042` -> `T045` -> `T046`
5. `T049` -> `T051` -> `T054` -> `T056` -> `T059`

This path is the minimum sequence to reach a working, observable Phase 4 MVP with deterministic fallback safety.

---

## Defer For Later

- vector / semantic memory overhaul
- reflective memory generation
- freeform long-horizon llm planning
- websockets
- auth
- cloud/distributed execution
- pygame / 2D embodiment
- multi-provider orchestration complexity
- advanced emotion engine

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Setup + Foundational.
2. Complete US1 routing, parser, fallback, and tick integration.
3. Validate deterministic, llm, and fallback behavior on one seeded scenario.
4. Freeze schema contract before observability/comparison expansion.

### Incremental Delivery

1. Setup + Foundational.
2. Deliver US1 and validate safety.
3. Deliver US2 observability/comparison.
4. Deliver US3 validation + docs.
5. Execute polish hardening and closeout.

### Single-Developer Agent-Assisted Flow

1. One coding agent handles tests/contracts first.
2. One coding agent handles core engine/parser modules.
3. Merge to tick integration, then observability/comparison, then docs.

---

## Notes

- `[P]` tasks are parallel-safe when file-level dependencies do not conflict.
- User-story tasks include required `[US#]` labels for traceability.
- Keep deterministic fallback mandatory for all llm/hybrid flows.
- Reject implementations that bypass world constraints or hide fallback reasons.

