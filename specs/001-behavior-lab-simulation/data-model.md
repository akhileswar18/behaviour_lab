# Data Model: Phase 3 Goal-Directed Situated Behavior

## Overview

Phase 3 extends the current social simulation with persisted goals, intentions, needs, zones,
resources, and interruption-aware planning. The model remains deterministic and replayable.

## Core Entities (Phase 3 scope)

## Goal

- Fields:
  - `id` (UUID, PK)
  - `agent_id` (UUID, FK -> Agent)
  - `scenario_id` (UUID, FK -> Scenario)
  - `goal_type` (string; examples: satisfy_hunger, seek_safety, cooperate, acquire_resource)
  - `priority` (float 0..1)
  - `status` (enum: active, deferred, completed, cancelled)
  - `target` (JSON object; zone/resource/agent target details)
  - `source` (string; need, world_event, social_context, scenario_seed)
  - `created_at` (datetime)
  - `updated_at` (datetime)
- Validation:
  - One `active` goal of a given `goal_type` per agent unless explicitly stacked.

## PlanState / Intention

- Fields:
  - `id` (UUID, PK)
  - `agent_id` (UUID, FK -> Agent)
  - `scenario_id` (UUID, FK -> Scenario)
  - `goal_id` (UUID, FK -> Goal, nullable)
  - `current_action_type` (string; move, acquire, consume, communicate, cooperate, avoid, observe, wait)
  - `status` (enum: active, interrupted, deferred, completed)
  - `rationale` (string)
  - `target_zone_id` (UUID, FK -> Zone, nullable)
  - `target_resource_id` (UUID, FK -> Resource, nullable)
  - `is_interruptible` (bool)
  - `started_at` (datetime)
  - `updated_at` (datetime)

## AgentStateSnapshot (Phase 3 extension)

- Added fields:
  - `hunger` (float 0..1)
  - `safety_need` (float 0..1)
  - `social_need` (float 0..1)
  - `zone_id` (UUID, FK -> Zone)
  - `inventory` (JSON object for simple resource counters)
- Requirements:
  - Needs change over time and after resource/social actions.
  - Location is persisted every tick to support zone occupancy replay.

## Zone

- Fields:
  - `id` (UUID, PK)
  - `scenario_id` (UUID, FK -> Scenario)
  - `name` (string)
  - `zone_type` (string; shelter, commons, storage, clinic)
  - `metadata` (JSON object)
  - `created_at` (datetime)
- Validation:
  - Unique zone name per scenario.

## Resource

- Fields:
  - `id` (UUID, PK)
  - `scenario_id` (UUID, FK -> Scenario)
  - `zone_id` (UUID, FK -> Zone)
  - `resource_type` (string; food, medicine, token)
  - `quantity` (int)
  - `status` (enum: available, low, depleted, reserved)
  - `created_at` (datetime)
  - `updated_at` (datetime)
- Validation:
  - `quantity >= 0`

## SimulationEvent (Phase 3 extension)

- Added event types:
  - `plan_change`
  - `interruption`
  - `move`
  - `acquire`
  - `consume`
  - `resource_shortage`
- Payload expectations:
  - include `goal_id`, `plan_state_id`, `zone_id`, `resource_id`, and causal references when available

## State Transitions (Phase 3)

1. Load current needs, active goals, plan state, zone occupancy, local resources, and recent events.
2. Retrieve relevant memories for the agent.
3. Evaluate whether the current plan should continue, defer, switch, or be interrupted.
4. Persist any goal or plan-state changes.
5. Execute one deterministic action:
   - `move`
   - `acquire`
   - `consume`
   - `communicate`
   - `cooperate`
   - `avoid`
   - `observe`
   - `wait`
6. Persist resulting state, resource changes, timeline events, and memory traces.

## Indexing Recommendations

- `Goal(scenario_id, agent_id, status, priority)`
- `PlanState(scenario_id, agent_id, status, updated_at)`
- `AgentStateSnapshot(agent_id, tick_number, zone_id)`
- `Zone(scenario_id, zone_type, name)`
- `Resource(scenario_id, zone_id, resource_type, status)`
- `SimulationEvent(scenario_id, tick_number, event_type, actor_agent_id, target_agent_id)`
