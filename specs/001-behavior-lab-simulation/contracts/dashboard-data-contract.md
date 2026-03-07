# Dashboard Data Contract - Phase 3 Goal-Directed Situated Behavior

## Purpose

Define the persisted-state query shapes required to inspect goals, needs, plans, zones,
resources, and interruptions in Phase 3.

## Views

## Agent Goal and Need View

- Inputs: `scenario_id`, optional `agent_id`
- Required fields:
  - `agent_id`
  - `current_zone_id`
  - `hunger`
  - `safety_need`
  - `social_need`
  - `active_goal_type`
  - `active_goal_priority`
  - `active_intention`
  - `intention_status`

## Goal / Plan History View

- Inputs: `scenario_id`, optional `agent_id`, optional `status`
- Required fields:
  - `goal_id`, `goal_type`, `priority`, `status`, `target`, `source`
  - `plan_state_id`, `current_action_type`, `rationale`, `target_zone_id`, `target_resource_id`

## Zone Occupancy View

- Inputs: `scenario_id`
- Required fields:
  - `zone_id`, `name`, `zone_type`, `occupants`, `visible_resources`

## Resource Availability View

- Inputs: `scenario_id`, optional `zone_id`, optional `resource_type`
- Required fields:
  - `resource_id`, `zone_id`, `resource_type`, `quantity`, `status`, `updated_at`

## Timeline/Event View

- Inputs: `scenario_id`, optional `agent_id`, optional `zone_id`, tick range, `event_type`
- Required event types:
  - `plan_change`
  - `interruption`
  - `move`
  - `acquire`
  - `consume`
  - `resource_shortage`
  - existing Phase 2 social event types
- Required fields:
  - `event_id`, `tick_number`, `event_type`, `actor_agent_id`, `target_agent_id`,
    `content`, `payload`, `created_at`

## Causal Chain Visibility Rule

The dashboard must support tracing:

`need -> goal -> intention -> action -> world/social effect`

for a selected agent or scenario path without reading source code.

## Contract Rules

- Dashboard reads persisted state only.
- Missing data returns empty collections rather than implicit fallbacks.
- Identifiers needed to correlate goals, plans, zones, resources, and timeline events must be present.
- Sorting defaults:
  - goals/plans: `updated_at DESC`
  - resources: `updated_at DESC`
  - timeline: `tick_number ASC`, `created_at ASC`
