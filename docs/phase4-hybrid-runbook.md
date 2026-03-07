# Phase 4 Hybrid Decision Runbook

## Purpose

Operate and troubleshoot the Phase 4 decision engine in `deterministic`, `llm`, and `hybrid` modes while preserving replayability and observability.

## Run Commands

1. Deterministic baseline

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run -H "Content-Type: application/json" -d "{\"ticks\":5,\"policy_mode\":\"deterministic\"}"
```

2. LLM mode

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run -H "Content-Type: application/json" -d "{\"ticks\":5,\"policy_mode\":\"llm\",\"llm_config\":{\"provider\":\"openai_compatible\",\"endpoint\":\"http://127.0.0.1:11434/v1/chat/completions\",\"model\":\"gpt-4o-mini\",\"timeout_seconds\":4.0}}"
```

3. Hybrid mode

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/run -H "Content-Type: application/json" -d "{\"ticks\":5,\"policy_mode\":\"hybrid\",\"llm_config\":{\"provider\":\"openai_compatible\",\"endpoint\":\"http://127.0.0.1:11434/v1/chat/completions\",\"model\":\"gpt-4o-mini\",\"timeout_seconds\":4.0}}"
```

## Expected Response Fields

- `policy_mode`
- `fallback_count`
- `llm_decision_count`
- `deterministic_decision_count`
- `tick_results`

## Fallback Diagnosis

When fallback occurs, inspect:

1. Decision logs for `decision_source=fallback_deterministic`
2. Decision log `parser_status` and `fallback_reason`
3. Timeline events with content `llm_fallback_triggered`
4. Timeline/system events with `llm_parse_status:*`

Common reasons:

- `timeout`
- `provider_error`
- `invalid_json`
- `schema_error`
- `illegal_action`
- `world_constraint`

## Comparison Workflow

Use `compare-rerun` with policy mode overrides:

```powershell
curl -X POST http://127.0.0.1:8000/scenarios/<scenario_id>/compare-rerun -H "Content-Type: application/json" -d "{\"ticks\":3,\"variant_name\":\"phase4-check\",\"base_policy_mode\":\"deterministic\",\"variant_policy_mode\":\"hybrid\"}"
```

Inspect returned deltas:

- `fallback_count_delta`
- `llm_decision_delta`
- `message_count_delta`
- `completed_goal_delta`
- `cooperation/conflict` deltas via comparison endpoint and dashboard

## Safety Rules

- Never disable deterministic fallback.
- Treat LLM output as proposal; world legality is authoritative.
- Do not trust responses that fail parse/schema/constraint checks.
- Keep deterministic mode as control arm for every experiment.
