# Research: Phase 3 Goal-Directed Situated Behavior

## Decision 1: Persist goals and intentions as first-class tables

- Decision: Store goals and active intentions in dedicated persisted models instead of deriving them from event history.
- Rationale: Goal continuity and interruption handling require direct, queryable state.
- Alternatives considered:
  - Infer goals from recent decisions only: too opaque and fragile for replay/debugging.
  - Store plans only in memory: violates observability and persistence requirements.

## Decision 2: Use a zone-based world instead of freeform coordinates

- Decision: Represent world grounding through named zones with simple occupancy and resource availability.
- Rationale: Zones provide location-dependent behavior without introducing pathfinding or physics complexity.
- Alternatives considered:
  - Continuous 2D coordinates: adds movement complexity without improving inspectability.
  - No world grounding: insufficient for resource-aware or situated behavior.

## Decision 3: Keep needs lightweight and deterministic

- Decision: Start with a small set of scalar needs such as `hunger`, `safety_need`, and optional `social_need`.
- Rationale: A narrow, explicit need model is easier to tune, persist, and explain.
- Alternatives considered:
  - Large emotional/drive systems: too complex for the current stage.
  - Goal-only planning without needs: weaker explanation for plan changes and interruptions.

## Decision 4: Layer planning on top of the existing decision loop

- Decision: Introduce a deterministic planning policy that selects continue/defer/switch/interrupt before final action selection.
- Rationale: This preserves the current simulation architecture and avoids a planner rewrite.
- Alternatives considered:
  - Replace the tick engine with a separate planner framework: unnecessary churn and higher failure risk.
  - Hardcode plans into scenario config only: too rigid for studying replanning behavior.

## Decision 5: Model resource interactions through explicit action events

- Decision: Resource acquire/consume/move outcomes should emit persisted events and update resource quantities directly.
- Rationale: Resource causality must be visible in the same replayable event stream as social effects.
- Alternatives considered:
  - Update resource counters silently: breaks auditability.
  - Batch resource updates outside ticks: hides immediate action consequences.

## Decision 6: Treat urgent events as interrupt signals, not full replanners

- Decision: Urgent world events and severe needs trigger deterministic interruption rules that replace or defer the current intention.
- Rationale: This produces clear, inspectable plan transitions while keeping rules understandable.
- Alternatives considered:
  - Freeform dynamic replanning: too magical for this phase.
  - Ignoring interruptions: fails the stated Phase 3 objective.
