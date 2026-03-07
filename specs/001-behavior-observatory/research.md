# Research: Phase 4 Hybrid Decision Engine

## Decision 1: Keep deterministic policy as hard baseline and fallback

- Decision: Deterministic policy remains first-class mode and mandatory fallback path for all LLM errors.
- Rationale: Preserves local reliability, reproducibility baseline, and constitution local-first requirements.
- Alternatives considered:
  - LLM-only mode with no fallback: too fragile under timeout/parse failures.
  - Retry-until-valid loop: increases latency and can stall tick progression.

## Decision 2: Insert explicit decision-engine abstraction in tick flow

- Decision: Add an intermediate `DecisionEngine` that routes to deterministic/llm/hybrid but always returns a single structured decision result.
- Rationale: Keeps tick engine stable while enabling policy experiments behind one interface.
- Alternatives considered:
  - Inline `if mode` logic in tick engine: raises coupling and test complexity.
  - Separate tick engine for llm mode: duplicates orchestration and breaks comparability.

## Decision 3: Enforce structured output contract for deterministic and llm paths

- Decision: Both policies emit the same typed decision schema (`action`, `intent`, `emotional_tone`, `confidence`, `rationale`, optional targets).
- Rationale: Allows one world execution pipeline and one observability contract.
- Alternatives considered:
  - Freeform text from LLM then heuristic mapping: fragile and hard to audit.
  - Separate schema per mode: complicates downstream execution and dashboards.

## Decision 4: Prompt builder uses bounded context windows

- Decision: Build prompts from persisted persona/state/goals/intentions/relationships/events/memory with deterministic truncation limits.
- Rationale: Controls latency/cost and keeps context inspectable and reproducible.
- Alternatives considered:
  - Dump full history: prompt bloat and non-deterministic token clipping.
  - Minimal context only: weak reasoning quality and persona drift.

## Decision 5: Validation stack must include world-constraint checks

- Decision: Validate parsed decision against schema and simulation constraints before execution.
- Rationale: Prevents impossible actions from bypassing world rules.
- Alternatives considered:
  - Schema-only validation: legal JSON can still be illegal in world state.
  - Execute-then-correct: introduces inconsistent transient state.

## Decision 6: Persist prompt/response metadata, not full payload by default

- Decision: Store prompt hash, compact context summary, parser status, and fallback reason by default; allow optional debug full capture.
- Rationale: Balances inspectability with storage and privacy concerns.
- Alternatives considered:
  - Store full prompts always: noisy storage and operational overhead.
  - Store no prompt metadata: weak root-cause observability.

## Decision 7: Integrate policy mode into run/comparison metadata

- Decision: Record policy mode and llm config per run and expose in comparison analytics.
- Rationale: Enables deterministic vs llm/hybrid behavior diffing and reproducible experiment trails.
- Alternatives considered:
  - Implicit mode from environment only: poor reproducibility.
  - Separate comparison pipeline: unnecessary divergence.
