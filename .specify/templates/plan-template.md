# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11 or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., FastAPI, Pydantic, SQLite or NEEDS CLARIFICATION]
**Storage**: [e.g., SQLite, files, PostgreSQL or N/A]
**Testing**: [e.g., pytest, contract tests, scenario tests or NEEDS CLARIFICATION]
**Target Platform**: [e.g., local desktop Python runtime, Linux dev box or NEEDS CLARIFICATION]
**Project Type**: [e.g., simulation engine + dashboard, service, library or NEEDS CLARIFICATION]
**Agent Scale Target**: [e.g., 2-5 agents in initial scenario or NEEDS CLARIFICATION]
**Time Model**: [e.g., tick-based, turn-based, hybrid or NEEDS CLARIFICATION]
**Observability Surface**: [e.g., dashboard panels + structured event logs or NEEDS CLARIFICATION]
**Performance Goals**: [domain-specific, e.g., 100 events/sec, <200ms decision step or NEEDS CLARIFICATION]
**Constraints**: [domain-specific, e.g., local-first, modular architecture, structured state]
**Scale/Scope**: [domain-specific, e.g., small social scenario, single machine, no cloud dependency]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] Behavior-first scope: design prioritizes cognition, memory, persona, communication, and observability over graphics polish.
- [ ] Python-first simplicity: each dependency addition is justified by behavior value, observability, or iteration speed.
- [ ] Modular architecture: cognition, memory, communication, orchestration, persistence, and visualization have clean interfaces.
- [ ] Observable-by-design: observations, memory operations, intentions, decisions, messages, and relationship updates emit structured traces.
- [ ] Memory and persona impact: feature design states how memory and persona influence runtime behavior.
- [ ] Communication consequences: communication flows define state, belief, goal, or relationship updates.
- [ ] State-over-time continuity: design defines tick/turn/time-step progression and persistence semantics.
- [ ] Structured schema discipline: critical entities/events use structured data contracts.
- [ ] Scenario-first validation: plan includes a reproducible scenario with explicit expected outcomes.
- [ ] Dashboard-first acceptance: feature is testable through dashboard views or structured logs without code spelunking.
- [ ] Local-first baseline: primary workflow runs locally without mandatory cloud services.
- [ ] Experiment readiness: plan enables comparative runs across persona, memory, prompt, or policy variants.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── cognition/
├── memory/
├── communication/
├── orchestration/
├── persistence/
└── visualization/

tests/
├── contract/
├── integration/
├── scenario/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (dashboard + backend)
backend/
├── src/
│   ├── cognition/
│   ├── memory/
│   ├── communication/
│   ├── orchestration/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── dashboard/
│   ├── timeline/
│   └── state_views/
└── tests/
```

**Structure Decision**: [Document the selected structure and reference the real directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., cloud dependency in prototype] | [current need] | [why local-first path cannot satisfy requirement] |
| [e.g., additional framework] | [specific problem] | [why lighter Python-first option is insufficient] |
