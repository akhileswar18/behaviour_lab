# Research: Phase 2 Social Dynamics

## Decision 1: Keep deterministic social interaction sequencing

- Decision: Maintain fixed per-tick agent ordering and deterministic update rules for message,
  relationship, and memory side effects.
- Rationale: Reproducibility is required for behavioral experiments and debugging.
- Alternatives considered:
  - Fully stochastic interaction policy first: richer emergence but weak explainability.
  - Async message/event handling: more realistic timing but harder to debug in local MVP.

## Decision 2: Use persisted social chain as source of truth

- Decision: Persist all message/relationship/decision transitions in DB and render dashboard from DB-only reads.
- Rationale: Enables traceability and avoids hidden in-memory behavior.
- Alternatives considered:
  - In-memory message bus only: lower latency but breaks replayability.
  - Hybrid in-memory + DB snapshots: increases complexity and drift risk.

## Decision 3: Persona influence as explicit weighted policy

- Decision: Use transparent persona trait weights (cooperation, risk, communication style,
  memory sensitivity) in decision policy outputs.
- Rationale: Keeps behavior differences inspectable and testable.
- Alternatives considered:
  - Free-form prompt-only persona behavior: less deterministic and weaker explainability.
  - Rule explosion per persona archetype: too rigid and hard to maintain.

## Decision 4: Relationship updates as evented state transitions

- Decision: Relationship changes are calculated by explicit update rules and mirrored as
  `relationship_update` SimulationEvents.
- Rationale: Supports causal inspection and auditable social dynamics.
- Alternatives considered:
  - Hidden relationship writes without events: lower visibility.
  - Batch-only relationship updates after run: delays feedback and complicates per-tick analysis.

## Decision 5: Add scenario event injection layer

- Decision: Introduce world/scenario events that can be scheduled per tick and consumed in the
  same event stream as agent actions.
- Rationale: Enables controlled social stimuli and comparison experiments.
- Alternatives considered:
  - No world events in Phase 2: limits experiment richness.
  - Complex simulation world model: out of scope and violates simplicity constraints.

## Decision 6: Strengthen contracts for social observability

- Decision: Extend API/dashboard contracts to include communication feeds, relationship history,
  scenario event injection, and filtered trace queries.
- Rationale: Ensures implementation and visualization evolve together.
- Alternatives considered:
  - Ad hoc endpoint additions: faster initially but weaker consistency and testability.
