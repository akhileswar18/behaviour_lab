# Feature Specification: Visual Behavior Observatory

**Feature Branch**: `[001-behavior-observatory]`
**Created**: 2026-03-06
**Status**: Draft
**Input**: User description: "Build a visual behavior observability system for the Behavior Lab simulation platform. The goal is to transform the existing table-based dashboard into a visual behavioral observatory that allows researchers and developers to understand agent cognition, social dynamics, and world evolution in real time. The dashboard must provide three distinct but connected views of the simulation: 1. Agent Intelligence View This view focuses on a single agent and exposes its internal cognitive state and behavioral drivers. The purpose is to answer the question: 'Why did this agent do what it did?' The Agent Intelligence View should show: agent identity and persona traits, current zone/location, internal needs, active goal and intention, plan progress and interruptions, decision traces with factor contributions, recalled memory influences, inventory and resource state, relationship summary with other agents, and interaction metrics. This view should visually represent needs, goals, and decision drivers using charts or gauges rather than tables. 2. Social Interaction View This view focuses on relationships and interactions between agents across the simulation. The purpose is to answer the question: 'How are agents influencing each other?' The Social Interaction View should show: live communication feed between agents, social network graph showing trust/affinity relationships, interaction metrics per agent, cooperation and conflict event counts, relationship change history, and causal chains linking interaction to relationship update to memory creation. 3. World Simulation View (God View) This view provides a macro-level overview of the entire simulation environment. The purpose is to answer the question: 'What is happening in the world right now?' The World Simulation View should show: current simulation tick and world state, global event feed, zone occupancy, resource distribution across zones, resource consumption events, global metrics such as average trust, goal completion rates, resource scarcity levels, and movement frequency, and a simplified world map showing zones, agents, and resources. The dashboard must remain fully consistent with the simulation's observability model. All visualizations must be derived from persisted data already recorded by the simulation system, including decision logs, events, memory traces, relationships, goals, and resources. The system must support filtering and inspection across ticks, agents, zones, and event types. The goal of this feature is to make the simulation explainable, inspectable, and suitable for behavioral analysis and experimentation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect One Agent Clearly (Priority: P1)

A researcher opens an individual agent view and can immediately understand that agent's current state, motivations, recent decisions, recalled memories, and performance signals without reading raw event tables.

**Why this priority**: The single-agent explanation view is the fastest path to answer the core question of behavioral analysis: why an agent acted the way it did.

**Independent Test**: Can be fully tested by running one scenario, opening one agent, and confirming the view explains current needs, active goal, active intention, recent decision factors, recalled memories, and recent outcomes using visual summaries rather than raw tables alone.

**Acceptance Scenarios**:

1. **Given** a scenario with persisted agent state, decisions, memories, and goals, **When** a user selects an agent, **Then** the dashboard shows the agent's identity, persona traits, current location, needs, active goal, active intention, inventory, and recent decision drivers in one connected view.
2. **Given** an agent with interruptions or plan changes in its history, **When** a user inspects that agent, **Then** the view clearly shows when the plan changed, what interrupted it, and how the current state differs from the previous one.
3. **Given** an agent with recalled memories influencing decisions, **When** the user inspects recent decisions, **Then** the view shows which recalled memories were associated with those decisions and how strongly they influenced the outcome.

---

### User Story 2 - Understand Social Dynamics (Priority: P2)

A researcher opens a social interaction view and can see how agents are influencing each other through communication, trust changes, cooperation, conflict, and downstream memory effects.

**Why this priority**: The simulation is intended to study social behavior over time, so users must be able to inspect interaction patterns and relationship change, not just individual cognition.

**Independent Test**: Can be fully tested by running a multi-agent scenario and confirming the dashboard displays communication activity, relationship structure, interaction counts, and causal chains from interaction to relationship change to memory creation.

**Acceptance Scenarios**:

1. **Given** a scenario with multiple communication and relationship events, **When** a user opens the social interaction view, **Then** the view shows current interaction activity, relationship strength between agents, and historical relationship change.
2. **Given** an interaction that leads to a relationship update and memory creation, **When** the user inspects that interaction, **Then** the view reveals the causal sequence from communication to relationship consequence to stored memory.
3. **Given** filters for agent, tick, and event type, **When** the user narrows the view, **Then** only relevant interaction and relationship information remains visible without breaking the causal story.

---

### User Story 3 - Observe the Whole World (Priority: P3)

A researcher opens a world-level view and can understand what is happening across the simulation right now, including where agents are, what resources are available, what events are unfolding, and whether the world is becoming more cooperative, scarce, or unstable.

**Why this priority**: Macro-level observability is necessary for experiment analysis, but it depends on the individual and social views already being grounded in persisted state and meaningful metrics.

**Independent Test**: Can be fully tested by running a scenario with multiple zones and resource changes, then confirming the dashboard shows current world state, zone occupancy, resource status, global metrics, and a simplified map of the scenario.

**Acceptance Scenarios**:

1. **Given** a scenario with multiple zones, agents, and resources, **When** a user opens the world simulation view, **Then** the view shows current tick, world events, zone occupancy, and resource distribution at the same point in time.
2. **Given** resource consumption and movement over multiple ticks, **When** a user inspects the world simulation view, **Then** the view shows where scarcity is emerging and how often agents are moving or consuming resources.
3. **Given** the user applies tick, zone, or event-type filters, **When** the world view refreshes, **Then** the displayed map, metrics, and event feed stay consistent with the filtered slice of the persisted simulation history.

### Edge Cases

- What happens when an agent has incomplete recent data, such as no recalled memories or no recent interactions?
- How does the observatory present conflicting signals, such as a cooperative message followed by a negative relationship update?
- What happens when a selected time range has no events for one or more views?
- How does the observatory handle a scenario where one zone has no agents or no resources?
- What happens when a scenario contains more tracked events than can be comfortably displayed at once?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an Agent Intelligence View centered on one selected agent.
- **FR-002**: The Agent Intelligence View MUST show the selected agent's identity, persona traits, current location, internal needs, active goal, active intention, inventory state, and relationship summary.
- **FR-003**: The Agent Intelligence View MUST show recent decision traces, plan progress, interruptions, recalled memory influences, and interaction metrics for the selected agent.
- **FR-004**: The Agent Intelligence View MUST present needs, goals, and decision drivers primarily through visual summaries such as gauges, charts, progress indicators, or similar non-tabular elements.
- **FR-005**: The system MUST provide a Social Interaction View centered on relationships and interactions across agents.
- **FR-006**: The Social Interaction View MUST show a live or near-current communication feed based on the latest persisted simulation state.
- **FR-007**: The Social Interaction View MUST show a visual network of agent relationships using persisted trust, affinity, or equivalent relationship strength data.
- **FR-008**: The Social Interaction View MUST show interaction metrics per agent, including message activity and counts of cooperative and conflict-oriented events.
- **FR-009**: The Social Interaction View MUST allow a user to inspect causal chains linking an interaction to the resulting relationship update and any associated memory creation.
- **FR-010**: The system MUST provide a World Simulation View that summarizes the current world state at a chosen tick or time slice.
- **FR-011**: The World Simulation View MUST show current tick, global event feed, zone occupancy, resource distribution, resource consumption history, and a simplified world map.
- **FR-012**: The World Simulation View MUST show global summary metrics, including average trust, goal completion rate, resource scarcity, and movement frequency.
- **FR-013**: All three views MUST derive their displayed information solely from persisted simulation records rather than hidden transient state.
- **FR-014**: The system MUST support filtering across ticks, agents, zones, and event types and apply those filters consistently across all relevant visualizations.
- **FR-015**: The system MUST allow users to move from summary visuals into supporting detail for the same data without leaving the selected scenario context.
- **FR-016**: The system MUST preserve traceability between decision logs, events, memory traces, relationships, goals, and resources when visualizing behavioral explanations.
- **FR-017**: The observatory MUST remain useful for both live simulation monitoring and post-run behavioral analysis.
- **FR-018**: The observatory MUST clearly distinguish current state from historical change so users can tell what is true now versus what changed over time.

### Key Entities *(include if feature involves data)*

- **Agent Observatory Profile**: The combined representation of one agent's identity, persona, needs, goals, intentions, memories, relationships, and activity metrics.
- **Decision Trace**: A persisted decision record plus the factors, influences, and outcomes needed to explain it visually.
- **Memory Influence Trace**: A persisted link between recalled memories and the decisions they informed.
- **Social Link**: A directed or undirected relationship between agents with current strength and change history.
- **Interaction Chain**: A sequence connecting communication, relationship updates, and resulting memory creation.
- **Zone Snapshot**: The occupancy and resource state of one zone at a selected moment.
- **World State Slice**: The aggregated state of the full simulation at a selected tick or filtered interval.

### Assumptions

- The feature builds on the existing persisted observability model and does not require users to inspect raw database records directly.
- Users analyze small-to-medium simulation runs where visual explanation is more important than maximizing event density on screen.
- The system may include supporting detail tables or lists, but the primary experience must be visual and analysis-oriented.
- Researchers need both current-state inspection and historical explanation within the same scenario session.

## Constitution Alignment *(mandatory)*

- **Behavior-first scope**: This feature strengthens understanding of cognition, memory, persona, communication, relationships, goals, and world state before any embodiment or graphics expansion.
- **Memory impact**: The feature exposes recalled memory influences and memory-creation consequences already captured by the simulation so users can inspect how memory affects behavior over time.
- **Persona impact**: The feature makes persona-visible differences explicit by surfacing persona traits alongside needs, decisions, goals, and interaction metrics for each agent.
- **Communication consequences**: The feature highlights how communication changes relationships, produces downstream memory effects, and contributes to cooperation or conflict patterns.
- **Observability plan**: The feature adds three connected observability surfaces: Agent Intelligence View, Social Interaction View, and World Simulation View, all backed by persisted decision, event, memory, relationship, goal, and resource records.
- **Scenario validation**: A small reproducible multi-agent scenario with goals, zones, relationships, and scarce resources is sufficient to validate that users can explain one agent, inspect interaction chains, and understand whole-world change.
- **Local-first execution**: The observatory remains usable in the local development environment and relies on persisted local simulation data rather than external services.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a standard three-agent scenario, a user can identify the selected agent's current needs, active goal, active intention, location, and most recent decision explanation within 30 seconds.
- **SC-002**: In the same scenario, a user can trace at least 90% of displayed major decisions to supporting persisted evidence such as decision factors, recalled memories, plan changes, or world events.
- **SC-003**: In a multi-agent run, a user can identify the strongest and weakest current social links and inspect their recent change history within 60 seconds.
- **SC-004**: In a multi-zone scenario, the world view shows zone occupancy, resource distribution, and global summary metrics for a selected tick with no contradictions across views.
- **SC-005**: For a filtered time slice, all three views update consistently so that a user inspecting the same scenario, tick range, and filters sees matching current-state and historical explanations.

## Implementation Notes

- The Agent Intelligence dashboard refactor now runs agent-first with optional scenario scoping.
- Overview mode and scenario mode are both supported through persisted-data analytics endpoints.
- Visual sections are implemented in the required A-G order with raw tables retained only as secondary detail views.
