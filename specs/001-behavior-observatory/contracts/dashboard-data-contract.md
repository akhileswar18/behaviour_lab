# Dashboard Data Contract: Phase 4 Decision Source Observability

## Scope

Phase 4 keeps existing dashboard pages but extends decision observability fields so deterministic and LLM-backed runs are comparable.

## Required Decision Fields for Dashboard/Analytics

Each decision row exposed to dashboard analytics must include:

- `decision_source` (`deterministic` | `llm` | `fallback_deterministic`)
- `parser_status`
- `fallback_reason` (nullable)
- `confidence`
- `rationale`
- action/intent/tone fields
- optional target fields

## Mode Metadata Contract

Run/session metadata surfaced in dashboard must include:

- `policy_mode`
- `llm_provider` (nullable)
- `llm_model` (nullable)
- `fallback_count`

## Timeline/Event Contract Additions

Timeline should expose (where present):

- `llm_parse_error`
- `llm_fallback`
- `decision_source`

## Comparison Contract Additions

Comparison views require policy-aware dimensions:

- deterministic vs llm/hybrid source distribution
- fallback-rate comparison
- action-mix and goal-completion deltas by policy mode

## Data Integrity Rules

- Values must be sourced from persisted records only.
- LLM metadata fields must not appear in deterministic-only rows unless explicitly null/defaulted.
- Fallback reason is required when `decision_source=fallback_deterministic`.

## Prompt/Response Retention Limits

- Default mode stores only `prompt_summary` and `prompt_hash` in decision logs.
- Raw prompt/response payloads are not required for dashboard rendering and are intentionally excluded by default.
- Debug prompt persistence may be enabled in config for local diagnostics only.
