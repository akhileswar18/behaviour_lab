---
description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Include test tasks for behavior, state transitions, and observability validation. Additional tests are optional if not required by spec.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline architecture

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project and baseline dependencies
- [ ] T003 [P] Configure linting, formatting, and type checking
- [ ] T004 [P] Define structured schemas for agent, memory, event, message, relationship, and tick in src/models/
- [ ] T005 Create local-first runtime configuration and docs for single-machine execution

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Implement simulation tick/turn loop and state progression engine in src/orchestration/
- [ ] T007 [P] Implement modular interfaces for cognition, memory, communication, and persistence
- [ ] T008 [P] Implement structured event logging pipeline for observability
- [ ] T009 Implement memory storage and retrieval primitives with timestamped attribution
- [ ] T010 Implement dashboard data access layer for state, memories, conversations, and relationships
- [ ] T011 Add baseline scenario harness for 2-5 agent reproducible runs in tests/scenario/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1

- [ ] T012 [P] [US1] Add scenario test for expected state transitions in tests/scenario/test_[name].py
- [ ] T013 [P] [US1] Add integration test for memory writes/retrievals in tests/integration/test_[name].py
- [ ] T014 [P] [US1] Add observability contract test for required events in tests/contract/test_[name].py

### Implementation for User Story 1

- [ ] T015 [P] [US1] Implement story-specific models/schemas in src/models/[file].py
- [ ] T016 [US1] Implement behavior/cognition logic in src/cognition/[file].py
- [ ] T017 [US1] Implement memory integration in src/memory/[file].py
- [ ] T018 [US1] Implement communication/state update path in src/communication/[file].py
- [ ] T019 [US1] Expose dashboard view model updates in src/visualization/[file].py
- [ ] T020 [US1] Document story-level local run and validation steps in specs/[###-feature-name]/quickstart.md

**Checkpoint**: User Story 1 is fully functional and independently testable

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2

- [ ] T021 [P] [US2] Add scenario test for persona-driven behavior differences in tests/scenario/test_[name].py
- [ ] T022 [P] [US2] Add integration test for communication consequences in tests/integration/test_[name].py

### Implementation for User Story 2

- [ ] T023 [P] [US2] Implement/extend persona logic in src/cognition/[file].py
- [ ] T024 [US2] Implement relationship update logic in src/orchestration/[file].py
- [ ] T025 [US2] Extend dashboard traces for story outcomes in src/visualization/[file].py

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3

- [ ] T026 [P] [US3] Add scenario regression test for multi-agent timeline behavior in tests/scenario/test_[name].py
- [ ] T027 [P] [US3] Add observability completeness test in tests/integration/test_[name].py

### Implementation for User Story 3

- [ ] T028 [P] [US3] Implement story-specific policy/strategy in src/communication/[file].py
- [ ] T029 [US3] Implement memory strategy experiment hook in src/memory/[file].py
- [ ] T030 [US3] Add dashboard comparison panel or trace view in src/visualization/[file].py

**Checkpoint**: All user stories are independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T031 [P] Documentation updates in docs/ and spec artifacts
- [ ] T032 Code cleanup and modular refactoring
- [ ] T033 [P] Performance profiling for simulation tick loop
- [ ] T034 [P] Expand unit test coverage for core modules in tests/unit/
- [ ] T035 Validate quickstart and reproducibility on a clean local setup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational; defines MVP behavior loop
- **User Story 2 (P2)**: Starts after Foundational; integrates with US1 but remains independently testable
- **User Story 3 (P3)**: Starts after Foundational; extends behavior without breaking prior stories

### Within Each User Story

- Tests for behavior/state/observability first
- Schema/model updates before service logic
- Service logic before dashboard wiring
- Story complete before moving to next priority

### Parallel Opportunities

- Setup and Foundational tasks marked [P] can run in parallel
- Test tasks within a story marked [P] can run in parallel
- Different user stories can be worked in parallel after Foundational

---

## Parallel Example: User Story 1

```bash
Task: "Add scenario test for expected state transitions in tests/scenario/test_[name].py"
Task: "Add integration test for memory writes/retrievals in tests/integration/test_[name].py"
Task: "Add observability contract test for required events in tests/contract/test_[name].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. STOP and VALIDATE: Verify behavior, memory, communication, and dashboard traces locally
5. Demo MVP before adding complexity

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 -> validate independently -> demo
3. Add User Story 2 -> validate independently -> demo
4. Add User Story 3 -> validate independently -> demo

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. After Foundational:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Merge with scenario regression and observability checks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each story must remain independently completable and testable
- Prefer modular changes over monolithic edits
- Reject tasks that hide behavior effects from dashboard/log traces
