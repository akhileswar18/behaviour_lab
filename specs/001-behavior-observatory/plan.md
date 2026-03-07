# Implementation Plan: Phase 4 Hybrid Decision Engine

**Branch**: `001-behavior-observatory` | **Date**: 2026-03-06 | **Spec**: `C:\Users\akhil\behaviour_lab\specs\001-behavior-observatory\spec.md`
**Input**: Add optional LLM-backed decision policy with deterministic fallback and full observability.

## Summary

Phase 4 introduces a hybrid decision engine on top of the existing deterministic simulation loop.
The deterministic policy remains the baseline and hard fallback. LLM reasoning is optional, schema-bound,
and subordinate to world constraints, persistence ordering, and replay/debug requirements.

Primary outcome: each tick routes through a decision engine (`deterministic`, `llm`, or `hybrid`) that emits
one shared structured decision object, with parse/validation/fallback telemetry persisted for analysis and
comparison reruns.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Streamlit, SQLModel, Pydantic, pydantic-settings, pytest, httpx/openai-compatible client abstraction  
**Storage**: SQLite single-file persisted simulation state  
**Testing**: pytest unit + integration + scenario + contract + comparison regression  
**Target Platform**: Local desktop Python runtime  
**Project Type**: Simulation engine + API + dashboard observability platform  
**Agent Scale Target**: 2-5 agents in deterministic and hybrid comparison scenarios  
**Time Model**: Tick-based, persisted event order  
**Observability Surface**: Decision logs, simulation events, comparison summaries, dashboard analytics  
**Performance Goals**: Decision step remains stable under local runs; LLM timeout bounded and fallback completes tick without run failure  
**Constraints**: deterministic fallback always available, no websocket/auth/cloud-orchestration requirements, no vector memory, no freeform multi-step planner  
**Scale/Scope**: Decision layer extension only; no redesign of core world execution or memory architecture

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gate Review

- [x] Behavior-first scope: adds cognition path, not graphics scope.
- [x] Python-first simplicity: adds minimal provider abstraction and structured parser.
- [x] Modular architecture: inserts decision engine boundary without replacing tick engine.
- [x] Observable-by-design: prompt metadata, parse status, source, fallback reason all persisted.
- [x] Memory and persona impact: prompt context explicitly carries memory + persona factors.
- [x] Communication consequences: final action still flows through existing communication/world update pipeline.
- [x] State-over-time continuity: tick sequencing and persistence order unchanged.
- [x] Structured schema discipline: deterministic and LLM paths share one typed decision schema.
- [x] Scenario-first validation: includes deterministic vs llm vs hybrid scenario comparisons.
- [x] Dashboard-first acceptance: decision source/fallback visibility included in analytics outputs.
- [x] Local-first baseline: deterministic mode remains fully local with no model dependency.
- [x] Experiment readiness: run-level policy overrides and provider config captured for reruns.

## Project Structure

### Documentation (this feature)

```text
specs/001-behavior-observatory/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── api.openapi.yaml
    └── decision-engine-contract.md
```

### Source Code (repository root)

```text
app/
├── agents/
│   ├── decision_policy.py
│   ├── llm_policy.py                 # new
│   ├── decision_engine.py            # new
│   ├── prompt_builder.py             # new
│   └── response_parser.py            # new
├── simulation/
│   ├── tick_engine.py                # updated integration point
│   └── runner.py                     # policy mode/run override plumbing
├── persistence/
│   ├── models.py                     # decision metadata extensions
│   └── repositories/
│       └── run_repository.py         # optional run config metadata helpers
├── api/
│   ├── routes/
│   │   └── simulation.py             # mode override + run controls
│   └── schemas/
│       └── api.py                    # request/response policy-mode fields
└── analytics/
    └── comparison_analytics.py       # deterministic vs llm/hybrid diff dimensions

tests/
├── unit/
│   ├── test_prompt_builder.py
│   ├── test_response_parser.py
│   └── test_decision_engine.py
├── integration/
│   ├── test_llm_fallback.py
│   └── test_policy_mode_routing.py
├── scenario/
│   └── test_phase4_policy_compare.py
└── contract/
    └── test_simulation_policy_contract.py
```

**Structure Decision**: Extend current modules in-place with a narrow decision-engine seam between context assembly and action execution.

## Phase 0: Outline & Research

### Unknowns Extracted

- Unknown 1: How to constrain LLM authority so world rules remain canonical.
- Unknown 2: How much prompt/response detail to persist for inspectability without bloating storage.
- Unknown 3: How to keep deterministic comparison quality when LLM path fails or times out.

### Research Tasks Dispatched

- Task: Research schema-first LLM output enforcement patterns for simulation decisions.
- Task: Research timeout/retry/fallback best practices for local synchronous agent loops.
- Task: Research prompt-compaction strategies for persona + memory + relationship contexts.
- Task: Research experiment design for deterministic vs llm vs hybrid run comparability.

### Consolidated Research Decisions

1. Use strict typed decision schema with parser/validator before any world action is applied.
2. Enforce hard timeout and zero-or-one retry in llm mode; fallback to deterministic on any failure.
3. Persist prompt metadata and compact summaries by default; store full prompt/response only in explicit debug mode.
4. Keep deterministic policy as both baseline mode and runtime fallback implementation.
5. Record decision source (`deterministic`, `llm`, `fallback`) and fallback reason per decision log row.

## Phase 1: Design & Contracts

### A. Decision Engine Abstraction

Introduce `DecisionEngine` service with signature:

- input: `DecisionContext`, `policy_mode`, `llm_config`, `constraints`
- output: `StructuredDecisionResult`

Modes:

- `deterministic`: current policy only
- `llm`: llm policy first, deterministic fallback on validation/runtime failure
- `hybrid`: deterministic pre-score + llm proposal + deterministic validator/fallback

Routing priority:

1. run override
2. scenario default
3. global default (`deterministic`)

### B. LLM Integration Layer

`llm_policy.py` responsibilities:

- call provider through provider-agnostic client wrapper
- enforce timeout budget
- return raw model text + token/meta usage
- no direct world mutation

Provider config in settings:

- provider name
- model name
- timeout seconds
- max tokens
- temperature (default conservative)
- debug_prompt_logging flag

### C. Prompt Builder Design

`prompt_builder.py` composes bounded context blocks:

- persona traits + style
- current needs/mood/state
- active goal + intention
- zone + local resources
- recent world events
- relationship summary
- recalled memory summary
- recent decision summary
- allowed action set and schema instructions

Prompt budget controls:

- top-N memories by relevance
- top-N recent events
- fixed-length relationship summary
- deterministic truncation order for reproducibility

### D. Structured Output Contract

Single schema (shared by deterministic and llm outputs):

- `action`
- `intent`
- `emotional_tone`
- `confidence`
- `rationale`
- optional `target_agent_id`, `target_zone_id`, `target_resource_id`

Parser flow:

1. parse json block
2. schema validate
3. world-constraint validate (possible action, valid target, resource feasibility)
4. if any failure -> deterministic fallback with explicit reason code

### E. Fallback and Safety

Fallback triggers:

- timeout
- provider error
- parse failure
- schema failure
- illegal action/target
- world constraint conflict

Fallback behavior:

- compute deterministic decision in same tick
- persist source as `fallback_deterministic`
- persist machine-readable fallback reason and parser status
- continue tick without exception propagation

### F. Comparison / Experiment Integration

Extend run metadata and comparison endpoints with:

- `policy_mode`
- `llm_provider`
- `llm_model`
- `fallback_count`
- decision-source distribution

Comparison views include:

- action mix deltas
- cooperation/conflict deltas
- interruption deltas
- goal completion deltas
- fallback rate

### G. Observability and Logging

Decision log extensions:

- decision source
- parser status
- fallback reason
- prompt hash / prompt summary metadata
- provider/model/latency metadata

Simulation events:

- `decision_source`
- `llm_parse_error`
- `llm_fallback`

Dashboard additions (existing observability surfaces):

- filter by decision source
- show fallback badge/reason
- compare deterministic vs llm/hybrid distributions

### H. Phased Implementation Roadmap (inside Phase 4)

1. Schema + abstraction
   - add structured decision schema and engine interfaces
2. Prompt + parser
   - implement bounded prompt builder and strict parser/validator
3. LLM policy + fallback
   - provider integration with timeout, fallback, and metadata
4. Tick integration
   - route tick decisions through engine while preserving world update order
5. API + run config
   - add policy mode overrides in run/start/compare flows
6. Observability + comparison
   - persist source/fallback telemetry and expose in analytics
7. Validation
   - unit/integration/scenario/contract tests for all modes and failure paths

### Risks, Tradeoffs, and What to Avoid

- Risk: nondeterminism degrades reproducibility.
  - Mitigation: deterministic mode always available; store run config + seed + mode metadata.
- Risk: invalid model output stalls simulation.
  - Mitigation: hard timeout + parser validation + deterministic fallback.
- Risk: prompt bloat harms latency and cost.
  - Mitigation: strict context budgets and summary-first prompt assembly.
- Risk: hidden model behavior reduces inspectability.
  - Mitigation: persist source, rationale, parser/fallback metadata, and structured traces.

Avoid:

- granting model direct world mutation authority
- removing deterministic baseline
- introducing vector memory or freeform planner scope in this phase
- adding infra complexity (websocket/auth/cloud orchestration)

### Acceptance Criteria

1. Tick engine can run in `deterministic`, `llm`, and `hybrid` modes without breaking event ordering.
2. Deterministic and LLM paths emit one shared structured decision schema.
3. Any LLM timeout/parse/validation/constraint failure falls back cleanly in the same tick.
4. Decision logs include source, parser status, and fallback reason where relevant.
5. Scenario reruns can compare deterministic vs llm/hybrid behavior with policy metadata visible.
6. Dashboard/analytics can filter and inspect decision-source and fallback telemetry.
7. Full local test suite for unit/integration/scenario/contract coverage passes.

### Post-Design Constitution Re-Check

- [x] Behavior-first and observability-first priorities preserved.
- [x] Deterministic baseline preserved for local-first reliability.
- [x] Modular boundaries remain explicit (engine/prompt/parser/provider).
- [x] Scenario comparison readiness improved with mode-aware telemetry.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Optional external model provider | Needed to test LLM cognition path | Deterministic-only cannot satisfy phase objective |

## Delivery Notes (2026-03-06)

- Decision engine seam implemented in `app/agents/decision_engine.py` with `deterministic`, `llm`, and `hybrid` routing.
- Structured decision contract implemented in `app/schemas/decision_engine.py` and used by both deterministic and LLM paths.
- Prompt builder, model adapter, and response parser implemented with bounded context and legality checks.
- Tick engine now persists `decision_source`, `parser_status`, `fallback_reason`, prompt summary/hash metadata, and LLM metadata.
- Run API supports `policy_mode` + `llm_config` overrides and returns fallback/source counts.
- Comparison reruns now support policy overrides and include `fallback_count_delta` and `llm_decision_delta`.
- Agent observability payloads expose decision-source/fallback details and source-aware KPI metrics.
- Phase 4 unit/integration/scenario/contract/smoke tests added and passing.
