# Decision Engine Contract (Phase 4)

## 1. Decision Engine Interface

`resolve(context, policy_mode, llm_config, constraints) -> StructuredDecisionResult`

### Inputs

- `context`: bounded tick context (persona, needs, goals, intention, location/resources, relationships, memories, recent events)
- `policy_mode`: `deterministic | llm | hybrid`
- `llm_config`: optional model/provider parameters
- `constraints`: allowed actions and world validity rules

### Output

`StructuredDecisionResult` (required fields)

- `action`
- `intent`
- `emotional_tone`
- `confidence`
- `rationale`
- optional targets: `target_agent_id`, `target_zone_id`, `target_resource_id`
- metadata: `decision_source`, `parser_status`, `fallback_reason`, `provider_latency_ms`

## 2. Prompt Contract

Prompt builder must include compact sections:

1. persona
2. internal state (needs/mood)
3. active goal/intention
4. zone + local resources
5. relationship summary
6. recalled memory summary
7. recent events summary
8. allowed actions + strict output schema instructions

Budget rules:

- deterministic top-N truncation
- stable ordering of events/memories
- explicit omission markers when truncated

## 3. LLM Response Contract

Expected JSON object:

```json
{
  "action": "cooperate",
  "intent": "propose",
  "emotional_tone": "supportive",
  "confidence": 0.72,
  "rationale": "Short reason tied to context.",
  "target_agent_id": "optional-uuid",
  "target_zone_id": "optional-uuid",
  "target_resource_id": "optional-uuid"
}
```

## 4. Validation and Fallback Rules

Validation order:

1. parse JSON
2. schema validation
3. constraint/world validation

On failure:

- run deterministic policy immediately
- set `decision_source=fallback_deterministic`
- set `parser_status` and `fallback_reason`
- persist fallback metadata and continue tick

## 5. Persistence/Observability Rules

Each persisted decision must include:

- source mode (`deterministic`, `llm`, `fallback_deterministic`)
- parse/validation status
- fallback reason if any
- prompt hash + compact prompt summary
- provider/model/latency metadata when llm/hybrid used

Optional debug mode may persist full prompt/response payloads.

## 6. Comparison Contract

Run metadata must expose:

- `policy_mode`
- provider/model identifiers
- fallback count
- decision-source distribution

Comparison outputs must support deterministic vs llm/hybrid diffing without changing baseline metrics schema.
