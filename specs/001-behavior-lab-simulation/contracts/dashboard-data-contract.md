# Dashboard Data Contract - Phase 2 Social Dynamics

## Purpose

Define persisted-state query shapes for social observability in Phase 2.

## Views

## Communication Feed View

- Inputs: `scenario_id`, optional `agent_id`, `tick_from`, `tick_to`
- Required fields:
  - `message_id`, `tick_number`, `sender_agent_id`, `receiver_agent_id`,
    `intent`, `emotional_tone`, `content`, `created_at`

## Relationship State View

- Inputs: `scenario_id`, optional `agent_id`
- Required fields:
  - `source_agent_id`, `target_agent_id`, `trust_score`, `affinity_score`,
    `stance`, `last_interaction_at`, `last_updated_tick`, `updated_at`

## Agent Detail Social Context View

- Inputs: `scenario_id`, `agent_id`
- Required sections:
  - Persona factors used in latest decision
  - Recent incoming/outgoing messages
  - Relationship rows involving selected agent
  - Recent/recalled memory records linked to social events

## Timeline/Event View

- Inputs: `scenario_id`, optional `agent_id`, `tick range`, `event_type`
- Required event types:
  - `world_event`, `decision`, `message`, `relationship_update`, `memory_write`
- Required fields:
  - `event_id`, `tick_number`, `event_type`, `actor_agent_id`, `target_agent_id`,
    `content`, `payload`, `created_at`

## Causal Chain Visibility Rule

The dashboard must support tracing:

`scenario/world event -> decision -> message -> relationship update -> memory write`

for at least one selected agent path without reading source code.

## Contract Rules

- Dashboard reads persisted state only (no in-memory-only data).
- Missing data returns empty lists, not null graph fragments.
- All records expose identifiers required for cross-table traceability.
- Sorting defaults: `tick_number ASC`, `created_at ASC`.
