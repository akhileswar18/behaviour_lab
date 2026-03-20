# Feature Specification: Embodied World Visual Quality Fix

**Feature Branch**: `003-embodied-world-visual-fix`  
**Created**: 2026-03-20  
**Status**: Draft  
**Input**: User description: "Fix the embodied world so it renders as a believable pixel-art house instead of debug placeholders, while keeping the existing backend spatial systems unchanged."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See a Real House World (Priority: P1)

A researcher opens the embodied world viewer and sees a furnished multi-room house with recognizable room layouts, walls, doors, and objects instead of wireframe boxes and empty dark space.

**Why this priority**: The current viewer fails the basic promise of embodied observation because the world itself is not visually legible.

**Independent Test**: Open the embodied world viewer without running new ticks and confirm the static environment is understandable as a house with distinct rooms and furnishings.

**Acceptance Scenarios**:

1. **Given** an embodied scenario is available, **When** the viewer loads, **Then** the environment shows a furnished house with visible room boundaries, doors, floors, and objects rather than placeholder rectangles.
2. **Given** the shared world map asset is available, **When** the viewer renders the scene, **Then** the visible environment matches the same room structure used for embodied navigation.
3. **Given** a required environment art asset is unavailable, **When** the viewer loads, **Then** the viewer falls back to a readable placeholder layout and clearly signals that a visual fallback is in use.

---

### User Story 2 - Watch Agents as Characters (Priority: P2)

A researcher watches agents move through the house as visually distinct pixel-art characters instead of identical colored dots.

**Why this priority**: Once the world is visible, the next essential step is making agents readable as characters with clear identity and motion.

**Independent Test**: Run a short multi-agent scenario and verify each agent appears as a distinct character and remains selectable throughout movement.

**Acceptance Scenarios**:

1. **Given** multiple agents are present in the scenario, **When** the viewer renders them, **Then** each agent appears as a distinct character rather than a generic marker.
2. **Given** an agent changes movement direction, **When** the viewer updates its motion, **Then** the character presentation reflects the movement direction rather than remaining visually static.
3. **Given** an agent-specific character asset is missing, **When** the viewer renders that agent, **Then** the system uses a clear fallback visual that preserves identity and selection behavior.

---

### User Story 3 - Understand Conversations and Thoughts In World (Priority: P3)

A researcher can quickly understand what agents are saying and thinking through readable in-world overlays rather than raw debug strings.

**Why this priority**: Social and cognitive behavior is a core research value of the system, and the current debug overlays make that behavior hard to interpret.

**Independent Test**: Run a scenario with conversation and decision rationale, then verify that dialogue and thought overlays are readable, visually distinct, and brief enough to scan in real time.

**Acceptance Scenarios**:

1. **Given** an agent speaks during a tick, **When** the world updates, **Then** a readable speech overlay appears above the speaker using concise human-readable text.
2. **Given** an agent exposes a thought or rationale, **When** the world updates, **Then** the viewer shows a thought overlay visually distinct from speech.
3. **Given** overlay text is too long for in-world display, **When** it is rendered, **Then** the content is shortened without breaking readability.

---

### User Story 4 - Inspect an Agent Through a Polished Detail Panel (Priority: P4)

A researcher selects an agent and sees a visually structured detail panel with needs, current goal, recent decisions, and conversation history instead of unstyled text blocks.

**Why this priority**: The side panel is the main interpretation surface for researchers who need to connect world behavior with agent state.

**Independent Test**: Select an agent after several ticks and confirm the panel presents current needs, active goal, recent decisions, and recent messages in an organized, scrollable layout.

**Acceptance Scenarios**:

1. **Given** an agent is selected, **When** the detail panel opens, **Then** needs are shown as clear visual indicators rather than plain percentages.
2. **Given** the selected agent has an active goal, **When** the panel renders, **Then** the goal is presented as a clearly separated summary card.
3. **Given** multiple decisions and recent messages exist, **When** the panel renders, **Then** the user can review them in a readable chronological list without the panel becoming unusable.

---

### User Story 5 - Watch Smooth Movement Instead of Teleporting (Priority: P5)

A researcher sees agents move smoothly between positions so the world feels embodied rather than tick-snapped.

**Why this priority**: Even with better art, teleporting movement breaks the illusion of presence and makes room transitions hard to follow.

**Independent Test**: Run a scenario with agents crossing multiple tiles and verify that position changes appear as continuous movement during the interval between authoritative ticks.

**Acceptance Scenarios**:

1. **Given** an agent changes position between ticks, **When** the viewer animates the update, **Then** the agent moves smoothly from the prior position to the new position rather than jumping instantly.
2. **Given** an agent stops moving, **When** interpolation completes, **Then** the agent settles into a stationary presentation instead of appearing to continue moving.
3. **Given** live ticks continue arriving during playback, **When** the viewer is in live mode, **Then** movement remains visually continuous across successive updates.

---

### User Story 6 - Experience Environmental Polish Without Losing Clarity (Priority: P6)

A researcher benefits from environmental cues such as time-of-day tinting, a readable minimap, and predictable camera behavior that make the world easier to follow.

**Why this priority**: These improvements add interpretability and polish once the core environment, agents, overlays, and movement are working.

**Independent Test**: Run a scenario across multiple time-of-day states and camera positions, then verify that the minimap, tinting, and camera controls improve orientation without obscuring the main scene.

**Acceptance Scenarios**:

1. **Given** the scenario time changes, **When** the world renders, **Then** the environment tint communicates time-of-day without reducing readability of agents or overlays.
2. **Given** the viewer shows a minimap, **When** agents move, **Then** their minimap positions remain aligned with the visible house layout.
3. **Given** the user has moved or followed the camera, **When** they choose to recenter, **Then** the camera returns to a predictable overview of the house.

### Edge Cases

- What happens when the house art asset is missing, incomplete, or cannot be rendered by the viewer?
- What happens when a character visual asset is missing for one specific agent?
- What happens when overlay text is too long to display clearly in-world?
- What happens when a scenario is still using zone-only behavior with no embodied world map?
- What happens when the world asset dimensions differ from the expected scale for the viewer?
- What happens when the minimap or environmental tint reduces readability during dense conversations?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST render the embodied world as a visually recognizable multi-room house rather than placeholder geometric room outlines.
- **FR-002**: The visible world MUST include enough environmental detail for a user to distinguish major rooms, doors, and furnishings at a glance.
- **FR-003**: The system MUST represent agents as distinct character visuals rather than identical generic markers whenever character assets are available.
- **FR-004**: The system MUST preserve agent selection and inspection behavior regardless of whether primary character visuals or fallback visuals are used.
- **FR-005**: The system MUST present speech and thought overlays as readable, visually distinct in-world elements rather than raw debug text.
- **FR-006**: The system MUST shorten or otherwise constrain overly long overlay text so the world remains readable during live observation.
- **FR-007**: The selected-agent detail panel MUST present needs, active goal, recent decisions, and recent conversation activity in a visually structured format.
- **FR-008**: The system MUST show needs using visual indicators that help users distinguish low, medium, and high urgency quickly.
- **FR-009**: The system MUST render movement between authoritative positions as smooth continuous motion rather than immediate teleportation.
- **FR-010**: The system MUST keep character motion visuals consistent with observed movement direction and stationary state.
- **FR-011**: The system MUST provide environmental orientation aids, including time-of-day visual cues and a readable minimap or equivalent overview aid.
- **FR-012**: The system MUST support predictable camera behavior for following activity and returning to an overview of the house.
- **FR-013**: The system MUST gracefully fall back to readable debug-safe visuals when required visual assets are missing or unusable.
- **FR-014**: The system MUST document attribution for any third-party visual assets used by the embodied world viewer.
- **FR-015**: The feature MUST preserve the current backend authority, message contracts, and embodied spatial behavior already validated in the existing embodied world.
- **FR-016**: The feature MUST leave the Streamlit dashboard workflow unchanged.

### Key Entities *(include if feature involves data)*

- **World Visual Asset**: The shared house environment asset used to display rooms, walls, doors, and furnishings for the embodied world.
- **Agent Visual Profile**: The visual identity for an agent, including default appearance, movement states, and fallback presentation.
- **Speech Overlay**: Short in-world dialogue text associated with one speaking agent for a limited time.
- **Thought Overlay**: Short in-world cognition text associated with one agent and visually distinct from speech.
- **Agent Detail View**: The selected-agent information surface containing needs, goals, decisions, and recent conversation context.
- **Motion Transition**: The visual interpolation state between two authoritative agent positions.
- **Fallback Visual Mode**: The readable degraded presentation used when world or character assets are missing or incompatible.

### Assumptions

- Existing embodied-world backend behavior, authoritative tick snapshots, and spatial state remain valid and do not require redesign for this feature.
- The existing viewer already receives enough live data to support the desired visual improvements.
- Users will primarily observe small household scenarios with a limited number of agents, so clarity matters more than cinematic complexity.
- Third-party art assets can be sourced with licenses that allow repository use and attribution.

### Scope Boundaries

- This feature does not introduce new simulation logic, decision rules, or backend policy behavior.
- This feature does not add new dashboard workflows, new persistence concepts, or new real-time protocol types.
- This feature does not attempt procedural world generation, multiplayer editing, 3D rendering, or physics simulation.

## Constitution Alignment *(mandatory)*

- **Behavior-first scope**: This feature improves how existing embodied behavior is perceived and interpreted without adding new simulation mechanics.
- **Memory impact**: Memory behavior is not expanded; the feature only makes existing thought, rationale, and conversation outputs easier to read in the world and side panel.
- **Persona impact**: Persona-driven differences remain visible through improved character presentation, decision logs, and readable in-world thoughts.
- **Communication consequences**: Existing communication events become more observable through clearer overlays and transcript presentation, but no new communication state changes are introduced.
- **Spatial grounding**: The feature makes embodied space legible by showing a real house layout and clearer room context while preserving compatibility with existing embodied spatial data.
- **Renderer authority**: The viewer remains read-only; authoritative world state continues to come from the backend, with the renderer only smoothing and presenting those updates.
- **Observability plan**: Validation relies on the embodied world viewer showing the furnished house, readable overlays, smooth movement, the polished side panel, minimap cues, and visual fallbacks when assets are missing.
- **Scenario validation**: A small household scenario with 3-5 rooms and 2-5 agents is sufficient to validate world readability, motion clarity, overlays, and agent inspection.
- **Local-first execution**: The feature remains locally runnable through the existing backend plus browser viewer workflow and does not require cloud services.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a seeded embodied scenario, a first-time viewer can correctly identify at least 3 distinct rooms and their purpose from the browser view alone within 30 seconds.
- **SC-002**: In a 3-agent observation run, 100% of visible agents are distinguishable from one another without relying on debug labels alone.
- **SC-003**: During a conversation-heavy run, at least 90% of displayed speech and thought overlays are readable without exposing raw debug-formatted strings.
- **SC-004**: In a 10-tick movement run, users observe smooth continuous travel between positions for all movement actions rather than instantaneous teleports.
- **SC-005**: In a selected-agent inspection flow, users can find current needs, active goal, recent decisions, and recent conversation activity within 10 seconds.
- **SC-006**: If required art assets are unavailable, the viewer still loads into a readable fallback presentation rather than failing to display the embodied world.
