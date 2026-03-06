# Data Model: Phase 2 Social Dynamics

## Overview

Phase 2 extends the current persisted simulation model to support inspectable social behavior:
structured communication, relationship updates, persona-influenced decisions, and scenario events.

## Core Entities (Phase 2 scope)

## Message

- Fields:
  - `id` (UUID, PK)
  - `scenario_id` (UUID, FK -> Scenario)
  - `tick_number` (int)
  - `sender_agent_id` (UUID, FK -> Agent)
  - `receiver_agent_id` (UUID, FK -> Agent, nullable for broadcast)
  - `target_mode` (enum: direct, broadcast)
  - `content` (string)
  - `intent` (string; examples: propose, warn, cooperate, avoid)
  - `emotional_tone` (string; examples: neutral, supportive, tense, skeptical)
  - `intent_tags` (JSON array)
  - `created_at` (datetime)
- Validation:
  - `tick_number >= 0`
  - `target_mode=direct` requires `receiver_agent_id`
- Relationships:
  - Many-to-one with `Scenario`
  - Many-to-one with `Agent` (sender)
  - Optional many-to-one with `Agent` (receiver)

## Relationship

- Fields:
  - `id` (UUID, PK)
  - `scenario_id` (UUID, FK -> Scenario)
  - `source_agent_id` (UUID, FK -> Agent)
  - `target_agent_id` (UUID, FK -> Agent)
  - `trust_score` (float -1..1)
  - `affinity_score` (float -1..1)
  - `stance` (string; allied/neutral/hostile)
  - `influence` (float 0..1)
  - `last_interaction_at` (datetime, nullable)
  - `last_updated_tick` (int)
  - `updated_at` (datetime)
- Validation:
  - Directed pair unique per (`scenario_id`, `source_agent_id`, `target_agent_id`)
  - `source_agent_id != target_agent_id`

## SimulationEvent (Phase 2 extension)

- Fields:
  - `id` (UUID, PK)
  - `scenario_id` (UUID, FK -> Scenario)
  - `tick_number` (int)
  - `event_type` (enum: world_event, decision, message, relationship_update, memory_write, system)
  - `actor_agent_id` (UUID, nullable)
  - `target_agent_id` (UUID, nullable)
  - `content` (string summary)
  - `payload` (JSON object)
  - `created_at` (datetime)
- Requirements:
  - Payload includes causal references where available (decision_id, message_id, relationship_id).

## PersonaProfile (Phase 2 extension)

- Fields:
  - `id` (UUID, PK)
  - `label` (string)
  - `communication_style` (string)
  - `cooperation_tendency` (float 0..1)
  - `risk_tolerance` (float 0..1)
  - `memory_sensitivity` (float 0..1)
  - `emotional_bias` (float -1..1, optional)
  - `priority_weights` (JSON object)
  - `reaction_biases` (JSON object)
  - `created_at` (datetime)

## DecisionLog (Phase 2 extension)

- Fields:
  - `id` (UUID, PK)
  - `scenario_id` (UUID, FK -> Scenario)
  - `agent_id` (UUID, FK -> Agent)
  - `tick_number` (int)
  - `selected_action` (string)
  - `rationale` (string)
  - `confidence` (float 0..1)
  - `observed_event_ids` (JSON array)
  - `persona_factors` (JSON object; applied traits/weights)
  - `relationship_factors` (JSON object; key social context)
  - `world_event_factors` (JSON object; relevant scenario event context)
  - `created_at` (datetime)

## ScenarioEventInjection (new helper entity)

- Fields:
  - `id` (UUID, PK)
  - `scenario_id` (UUID, FK -> Scenario)
  - `tick_number` (int)
  - `event_key` (string)
  - `event_content` (string)
  - `payload` (JSON object)
  - `is_consumed` (bool)
  - `created_at` (datetime)
- Purpose:
  - Deterministically inject world/scenario stimuli into upcoming ticks.

## State Transitions (Phase 2)

1. Load scheduled world events for tick.
2. For each active agent:
   - Observe recent events.
   - Retrieve relevant memory.
   - Read relationship context.
   - Apply persona weighting.
   - Select social action and optional message.
3. Persist DecisionLog with explicit influence factors.
4. Persist Message and corresponding SimulationEvent (if communication action selected).
5. Apply relationship update rule and persist Relationship + relationship_update event.
6. Persist resulting memory writes and retrieval traces.
7. Persist TickResult.

## Indexing Recommendations

- `Message(scenario_id, tick_number, sender_agent_id, receiver_agent_id)`
- `Relationship(scenario_id, source_agent_id, target_agent_id, updated_at)`
- `SimulationEvent(scenario_id, tick_number, event_type, created_at)`
- `DecisionLog(scenario_id, tick_number, agent_id)`
- `ScenarioEventInjection(scenario_id, tick_number, is_consumed)`
