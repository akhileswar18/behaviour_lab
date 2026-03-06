<!--
Sync Impact Report
- Version change: 0.0.0-template -> 1.0.0
- Modified principles:
  - Template Principle Slot 1 -> I. Behavior-First Over Graphics-First
  - Template Principle Slot 2 -> II. Python-First Simplicity
  - Template Principle Slot 3 -> III. Modular Agent Architecture
  - Template Principle Slot 4 -> IV. Observable by Design
  - Template Principle Slot 5 -> V. Memory Is a First-Class System
  - Added VI-XVII as explicit principles for persona, communication, dashboard validation,
    scenario-driven iteration, state/time continuity, structured data, safe fast iteration,
    local-first development, experiment-friendly design, incremental complexity, AI-assisted
    code quality, and milestone success criteria.
- Added sections:
  - Engineering Constraints & Architectural Preferences
  - Quality Standards & Feature Acceptance Mindset
- Removed sections:
  - None
- Templates requiring updates:
  - ✅ updated: .specify/templates/plan-template.md
  - ✅ updated: .specify/templates/spec-template.md
  - ✅ updated: .specify/templates/tasks-template.md
  - ⚠ pending: .specify/templates/commands/*.md (directory not present in repository)
  - ⚠ pending: README.md and docs/quickstart.md (not present in repository)
- Follow-up TODOs:
  - None
-->

# Behaviour Lab Constitution

## Core Principles

### I. Behavior-First Over Graphics-First
All architecture and implementation decisions MUST prioritize agent cognition, memory,
persona, communication, and observability before embodiment, animation, or visual polish.
Early phases MUST avoid 3D or game-engine complexity unless it is strictly required to test a
behavioral hypothesis.
Rationale: The project exists to study agent behavior, not to optimize rendering fidelity.

### II. Python-First Simplicity
The platform MUST use a minimal Python-first stack with the smallest viable set of tools.
New dependencies MUST be justified by direct, documented value to agent behavior,
observability, or developer iteration speed.
Rationale: Simpler stacks reduce failure modes and preserve iteration velocity.

### III. Modular Agent Architecture
Agent cognition, memory, communication, orchestration, persistence, and visualization MUST
be separate modules with explicit interfaces. Implementations MUST support replacing memory
strategies, model providers, communication policies, and dashboard components without
rewriting the full system.
Rationale: Modular boundaries make experimentation and long-term maintenance feasible.

### IV. Observable by Design
Every significant agent step MUST be inspectable through structured telemetry. Observations,
memory writes and retrievals, intentions, decisions, messages, and relationship updates MUST
be recorded as queryable events.
Rationale: Hidden logic prevents scientific debugging and invalidates behavioral analysis.

### V. Memory Is a First-Class System
Memory MUST be treated as a core subsystem in all designs. Implementations MUST support
structured memory storage, retrieval, mutation, attribution, and timestamping so memory can
influence future reasoning.
Rationale: Persistent, actionable memory is foundational to believable longitudinal behavior.

### VI. Persona Must Influence Behavior
Persona definitions MUST drive communication style, priorities, emotional tendencies,
decision bias, and relationship formation. Persona metadata that does not affect runtime
behavior is non-compliant.
Rationale: Behavioral differentiation requires operational personas, not decorative profiles.

### VII. Communication Must Change State
Agent communication MUST be modeled as consequential events that can alter memory,
beliefs, goals, emotional state, and relationships. Display-only chat without state impact is
insufficient.
Rationale: Social simulation depends on communication as a causal mechanism.

### VIII. Dashboard-First Validation
A feature is complete only when its effects are visible in the dashboard or equivalent
structured traces. The interface MUST expose agent state, memory history, communication
flows, relationships, and timelines.
Rationale: Visual and structured inspection is required for fast behavioral verification.

### IX. Scenario-Driven Iteration
Development MUST proceed through small, explicit scenarios with clear event loops and
testable outcomes. Early scope MUST target 2-5 agents and one meaningful interaction before
expanding complexity.
Rationale: Controlled scenarios isolate behavior changes and reduce confounding variables.

### X. State and Time Matter
The simulation MUST model evolving internal state across ticks, turns, or time steps.
Stateless request-response designs that prevent continuity, relationship evolution, or
emergent dynamics are prohibited for core behavior flows.
Rationale: Continuity across time is required for social and memory-driven dynamics.

### XI. Structured Data Over Ad Hoc Text Blobs
Critical entities and events MUST use structured schemas for agents, memories, messages,
relationships, and decisions. Free text may be retained as supporting detail but cannot be the
sole representation of system-critical state.
Rationale: Structured data enables filtering, analysis, replay, and reproducibility.

### XII. Fast Iteration With Safety Rails
Rapid prototyping is encouraged, but each change MUST preserve modularity, debuggability,
and architectural clarity. Magic behavior, oversized files, fragile shortcuts, and hidden
cross-module coupling are disallowed.
Rationale: Speed without discipline destroys research reliability and team velocity.

### XIII. Local-First Development
Early-phase workflows MUST run locally with local storage and local inspection as default.
Cloud services MAY be optional extensions but MUST NOT be hard prerequisites for baseline
simulation and dashboard execution.
Rationale: Local-first operation lowers setup friction and supports rapid experimentation.

### XIV. Experiment-Friendly Design
The architecture MUST support controlled comparison of personas, memory strategies, prompts,
scenarios, and communication policies across repeated runs.
Rationale: The product is a behavioral lab, so comparative experimentation is a primary use
case.

### XV. Incremental Complexity
System capabilities MUST be introduced in phases: single-agent to multi-agent, static persona
to evolving relationships, basic memory to reflective memory, and basic dashboard to advanced
analytics. Complex world mechanics MUST NOT precede a stable cognition loop.
Rationale: Sequential complexity avoids premature architecture and protects learning cycles.

### XVI. Code Quality for AI-Assisted Development
Because coding agents may contribute frequently, the codebase MUST favor small files,
explicit naming, typed models where useful, clear contracts, concise docs, and predictable
implementation patterns that humans and agents can safely extend.
Rationale: AI-assisted development requires extra clarity to avoid compounding defects.

### XVII. Milestone Success Criteria
The first milestone is complete only when a working prototype demonstrates a small agent
population with distinct personas, memory storage and retrieval, consequential communication,
internal state updates from events, and dashboard-visible behavior.
Rationale: This milestone validates core research value before broader scope expansion.

## Engineering Constraints & Architectural Preferences

- Primary language and orchestration runtime MUST be Python.
- The initial product surface MUST be 2D and dashboard-first; game-style world simulation is
  deferred until cognition and observability loops are stable.
- Module boundaries MUST include, at minimum: `cognition`, `memory`, `communication`,
  `orchestration`, `persistence`, and `visualization`.
- State models MUST include explicit timestamps or tick identifiers for replayable timelines.
- Event and state records MUST be structured and versioned; schema changes MUST include
  migration notes.
- Data access and model-provider integrations MUST remain swappable behind interfaces.
- Local execution MUST be documented with minimal setup and without mandatory cloud accounts.

## Quality Standards & Feature Acceptance Mindset

- Feature proposals MUST include: targeted scenario, expected behavioral change, observability
  plan, and measurable acceptance signals.
- A feature MUST NOT be accepted unless behavior impact is visible in dashboard panels or
  structured logs.
- Every feature touching cognition, memory, communication, or relationships MUST define test
  coverage for state transitions and trace outputs.
- Pull requests MUST include architecture impact notes when module interfaces or schemas
  change.
- Anti-patterns to reject:
  - Graphics-driven scope creep before behavioral loop stability
  - Monolithic agent logic with hidden side effects
  - Memory represented only as unstructured prompts
  - Communication pipelines that do not update state
  - Opaque heuristics with no event-level traceability
  - One-off demo code that cannot support controlled experiment reruns

## Governance

This constitution is authoritative for architecture reviews, feature specs, implementation
plans, and task generation.

Amendment Process:
1. Propose a change with explicit rationale, impact scope, and migration requirements.
2. Record affected principles and whether the change is additive, clarifying, or breaking.
3. Obtain maintainer approval and update dependent templates or process docs in the same
   change.
4. Prepend a Sync Impact Report to this document describing propagated updates and pending
   follow-ups.

Versioning Policy:
- MAJOR: Backward-incompatible governance changes, principle removals, or principle
  redefinitions.
- MINOR: New principles, new mandatory sections, or materially expanded guidance.
- PATCH: Clarifications, wording improvements, and non-semantic refinements.

Compliance Review Expectations:
- Every spec, plan, and task set MUST include an explicit constitution check.
- Reviewers MUST block merges that violate MUST-level principles without an approved
  amendment.
- Exceptions MUST be time-bounded, documented, and tied to a follow-up amendment or
  remediation plan.

**Version**: 1.0.0 | **Ratified**: 2026-03-06 | **Last Amended**: 2026-03-06
