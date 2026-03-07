# Quickstart: Phase 4 Hybrid Decision Engine

## Prerequisites

- Local API and dashboard run normally in deterministic mode.
- Seed data and scenario runner already working.
- Optional provider credentials available only for llm/hybrid tests.

## 1. Baseline deterministic run

1. Run one seeded scenario for 8 ticks with `policy_mode=deterministic`.
2. Confirm decisions/events persist as baseline.

## 2. LLM mode run

1. Run the same scenario with `policy_mode=llm` and valid `llm_config`.
2. Verify decisions persist with `decision_source=llm` where parsing/validation succeeds.
3. Confirm tick loop continues if any single llm request fails.
4. Verify run response includes `fallback_count` and source counts.

## 3. Hybrid mode run

1. Run scenario with `policy_mode=hybrid`.
2. Verify final decision schema remains identical to deterministic mode.
3. Confirm fallback appears when model output is invalid or impossible.

## 4. Validate fallback paths

Force each failure mode and confirm deterministic fallback:

- timeout
- invalid json
- schema violation
- impossible action/target
- provider error

Expected result: no tick crash, fallback reason persisted.

## 5. Validate observability

Inspect persisted decision logs and timeline:

- decision source
- parser status
- fallback reason
- prompt summary/hash metadata
- provider/model/latency metadata

## 6. Validate comparison reruns

Run deterministic vs llm/hybrid variants and compare:

- action mix changes
- cooperation/conflict changes
- interruption deltas
- goal completion deltas
- fallback rate

Use `base_policy_mode` and `variant_policy_mode` in `compare-rerun` payload to override run policy.

## 7. Guardrail checks

- Deterministic mode works with no llm configuration.
- LLM mode never bypasses world constraints.
- No non-deterministic side effects appear before final validated decision persistence.
