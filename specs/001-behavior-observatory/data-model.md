# Data Model: Phase 4 Hybrid Decision Engine

## Scope

Phase 4 adds decision-engine, LLM metadata, and fallback observability models.
Core simulation entities remain unchanged.

## New/Extended Entities

### DecisionEngineConfig (run-level)

- Purpose: selects decision source behavior for a run/scenario.
- Fields:
  - `policy_mode` (`deterministic` | `llm` | `hybrid`)
  - `llm_provider` (optional)
  - `llm_model` (optional)
  - `timeout_seconds`
  - `max_tokens`
  - `temperature`
  - `debug_prompt_logging` (bool)
- Validation:
  - `policy_mode=deterministic` allows null provider/model
  - `policy_mode in (llm, hybrid)` requires provider+model
  - timeout must be >0

### StructuredDecision (shared contract)

- Purpose: normalized decision payload used by deterministic and llm policies.
- Fields:
  - `action` (enum from allowed action set)
  - `intent` (enum)
  - `emotional_tone` (enum)
  - `confidence` (0..1)
  - `rationale` (string)
  - `target_agent_id` (optional)
  - `target_zone_id` (optional)
  - `target_resource_id` (optional)
- Validation:
  - action must be executable in current world state
  - targets must exist and be legal for action

### DecisionResolutionMetadata (persisted with decision logs)

- Purpose: explain how final decision was produced.
- Fields:
  - `decision_source` (`deterministic` | `llm` | `fallback_deterministic`)
  - `parser_status` (`ok` | `invalid_json` | `schema_error` | `constraint_error` | `timeout` | `provider_error`)
  - `fallback_reason` (optional code/string)
  - `prompt_hash` (optional)
  - `prompt_summary` (optional compact context summary)
  - `provider_latency_ms` (optional)
  - `llm_provider` (optional)
  - `llm_model` (optional)

### PromptContextSnapshot (ephemeral + optional persisted debug)

- Purpose: bounded context used for llm reasoning.
- Fields:
  - `persona_summary`
  - `needs_state`
  - `mood`
  - `active_goal`
  - `active_intention`
  - `zone_context`
  - `resource_context`
  - `relationship_summary`
  - `memory_summary`
  - `recent_events_summary`
  - `allowed_actions`
- Validation:
  - deterministic truncation rules applied
  - no missing required sections for llm/hybrid mode

## Existing Entity Extensions

### DecisionLog (extension)

Add fields:
- `decision_source`
- `parser_status`
- `fallback_reason`
- `prompt_hash`
- `prompt_summary`
- `provider_latency_ms`
- `provider_name`
- `model_name`

### RunMetadata (extension)

Add fields:
- `policy_mode`
- `llm_provider`
- `llm_model`
- `llm_overrides` (json)
- `fallback_count`

### SimulationEvent (extension)

Add/standardize event types:
- `llm_parse_error`
- `llm_fallback`
- `decision_source`

## State Transitions

### Decision Resolution State

1. `context_ready`
2. `policy_selected`
3. `llm_attempted` (llm/hybrid only)
4. `parsed_valid` OR `parse_failed`
5. `constraint_valid` OR `constraint_failed`
6. `fallback_applied` (if needed)
7. `decision_persisted`
8. `action_executed`

Transition guarantees:
- one persisted final decision per agent per tick
- fallback path never skips persistence
- world updates occur only after final validated structured decision
