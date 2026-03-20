# Tasks: Embodied World Visual Quality Fix

**Input**: Design documents from `/specs/003-embodied-world-visual-fix/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Use manual browser verification plus targeted frontend Vitest coverage for interpolation, panel formatting, and renderer state mapping. Preserve existing backend embodied regression coverage when validating shared map assets.

**Organization**: Tasks are grouped by setup, foundational rendering, and user story so each visual slice remains independently verifiable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Every task includes exact file paths, dependencies, and expected outputs

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Complete the missing asset and map-design work before any renderer code changes begin.

- [X] T001 Download and place the chosen 16x16 indoor tileset in `client/public/assets/tilesets/interiors.png` [Deps: none] [Output: indoor tileset PNG available at the final Phaser load path]
- [X] T002 [P] Create or export three distinct 16x16 character spritesheets in `client/public/assets/tilesets/agents/agent_1.png`, `client/public/assets/tilesets/agents/agent_2.png`, and `client/public/assets/tilesets/agents/agent_3.png` [Deps: none] [Output: three directional walk-cycle spritesheets ready for Phaser loading]
- [X] T003 Design the furnished 40x30 five-room house in `maps/house.json` using Tiled layers `floor`, `walls`, `furniture`, `furniture_upper`, `collision`, and `objects` with zone rectangles for `kitchen`, `bedroom`, `living_room`, `bathroom`, and `commons` [Deps: T001] [Output: real Tiled JSON house map saved in the shared backend path]
- [X] T004 Copy the finalized Tiled export from `maps/house.json` to `client/public/assets/maps/house.json` [Deps: T003] [Output: identical client and shared house map JSON assets]
- [X] T005 [P] Document source, author, license, and download URL for every visual asset in `client/public/assets/ATTRIBUTION.md` [Deps: T001, T002] [Output: complete attribution record for tileset and character art]
- [X] T006 Verify `maps/house.json` loads cleanly against the existing parser contract in `app/simulation/tilemap_loader.py` and existing embodied tests [Deps: T003, T004] [Output: confirmed backend compatibility or a documented note if a minimal parser tweak is truly required]

**Checkpoint**: Opening `maps/house.json` in Tiled shows a furnished five-room house, all PNG assets exist in their final directories, and the backend can parse the exported map without errors.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Replace the placeholder room renderer with real tilemap loading before any agent, overlay, or panel polish work begins.

**CRITICAL**: No user story work should complete until this phase is done.

### Tests for Foundational Rendering

- [X] T007 [P] Add static tilemap scene coverage in `client/tests/world-scene.test.ts` for real-map loading, required layer creation, and rectangle fallback behavior [Deps: T004] [Output: failing scene-level tests for Tiled JSON loading and fallback rendering]
- [X] T008 [P] Validate `client/public/assets/maps/house.json` against `specs/003-embodied-world-visual-fix/contracts/tilemap-format-contract.md` [Deps: T004] [Output: confirmed layer names, dimensions, and zone metadata before renderer edits]

### Implementation for Foundational Rendering

- [X] T009 Update `client/src/game/scenes/Preloader.ts` to load `client/public/assets/maps/house.json`, `client/public/assets/tilesets/interiors.png`, and `client/public/assets/tilesets/agents/agent_1.png`, `client/public/assets/tilesets/agents/agent_2.png`, `client/public/assets/tilesets/agents/agent_3.png` with Phaser asset loaders [Deps: T002, T004, T007] [Output: Phaser preloader caches the real map, tileset image, and character spritesheets]
- [X] T010 Replace placeholder room drawing in `client/src/game/scenes/WorldScene.ts` with `this.make.tilemap({ key: "world-map" })`, `map.addTilesetImage(...)`, and tilemap layer creation for `floor`, `walls`, `furniture`, and `furniture_upper` [Deps: T009] [Output: the world scene renders the furnished pixel-art house instead of rectangles]
- [X] T011 Configure collision and camera bounds in `client/src/game/scenes/WorldScene.ts` from the `collision` layer and real tilemap dimensions [Deps: T010] [Output: collision tiles and camera limits align to the real house map]
- [X] T012 Run browser verification for static map rendering through `client/src/game/scenes/Preloader.ts` and `client/src/game/scenes/WorldScene.ts` [Deps: T011] [Output: confirmed furnished house renders correctly with no agent work yet]

**Checkpoint**: Opening the browser shows the pixel-art house with visible floors, walls, furniture, and camera bounds, with no fallback rectangles in the happy path.

---

## Phase 3: User Story 1 - See a Real House World (Priority: P1)

**Goal**: A researcher can open the embodied viewer and immediately understand the house layout instead of seeing wireframe rooms.

**Independent Test**: Load the client without running new ticks and confirm the environment reads as a furnished house with recognizable rooms and doorways.

### Tests for User Story 1

- [X] T013 [P] [US1] Add fallback and static-world verification notes to `specs/003-embodied-world-visual-fix/quickstart.md` for missing art, zone-only mode, and room readability checks [Deps: T012] [Output: explicit US1 validation checklist in the feature quickstart]
- [X] T014 [P] [US1] Add browser-scene regression assertions in `client/tests/world-scene.test.ts` for map bounds, layer order, and graceful asset fallback [Deps: T007, T011] [Output: failing US1 coverage for readable world rendering and fallback safety]

### Implementation for User Story 1

- [X] T015 [US1] Finalize room readability, layer ordering, and fallback signaling in `client/src/game/scenes/WorldScene.ts` [Deps: T014] [Output: stable real-house render path plus clear fallback behavior when map assets are missing]
- [X] T016 [US1] Update `client/src/game/scenes/Preloader.ts` to emit consistent load keys and fallback warnings for missing map or tileset assets [Deps: T015] [Output: predictable loader behavior for real-world and fallback map rendering]

**Checkpoint**: User Story 1 is independently verifiable: the embodied viewer shows a legible furnished house and degrades gracefully if required visual assets are missing.

---

## Phase 4: User Story 2 - Watch Agents as Characters (Priority: P2)

**Goal**: Researchers see distinct pixel-art characters on the map instead of purple circles.

**Independent Test**: Run a three-agent scenario for five ticks and verify each agent appears as a distinct selectable character at the correct tile position.

### Tests for User Story 2

- [X] T017 [P] [US2] Add sprite identity and tile-to-pixel mapping tests in `client/tests/agent-sprite.test.ts` [Deps: T009, T011] [Output: failing coverage for sprite-key assignment, scale, and tile coordinate conversion]
- [X] T018 [P] [US2] Extend `client/tests/useSimulationState.test.ts` to verify stable agent ordering and render-state mapping for distinct character selection [Deps: T009] [Output: failing state-mapping tests for character identity and selection continuity]

### Implementation for User Story 2

- [X] T019 [US2] Replace circle markers with sprite-based agents and animation registration in `client/src/game/sprites/AgentSprite.ts` [Deps: T017] [Output: agents render as 16x16 sprites scaled to 48px with interactive selection preserved]
- [X] T020 [US2] Map agent identities to spritesheet keys and spawn them on the real tilemap in `client/src/game/scenes/WorldScene.ts` [Deps: T018, T019] [Output: each live agent appears as a distinct pixel character at the correct tile position]
- [X] T021 [US2] Run live browser verification for sprite rendering through `client/src/game/sprites/AgentSprite.ts` and `client/src/game/scenes/WorldScene.ts` [Deps: T020] [Output: confirmed three-agent scenario shows distinct pixel characters instead of circles]

**Checkpoint**: Browser shows the furnished house populated by distinct pixel-art characters that remain selectable during live observation.

---

## Phase 5: User Story 3 - Understand Conversations and Thoughts In World (Priority: P3)

**Goal**: Conversations and rationales read as in-world overlays instead of raw debug strings.

**Independent Test**: Run a conversation-heavy scenario and verify that speech and thought overlays are readable, visually distinct, and truncated appropriately.

### Tests for User Story 3

- [X] T022 [P] [US3] Add overlay text formatting and truncation tests in `client/tests/overlay-ui.test.ts` [Deps: T020] [Output: failing coverage for 60-character truncation, wrapping, and first-sentence cleanup]
- [X] T023 [P] [US3] Extend `client/tests/useSimulationState.test.ts` to validate speech and thought payload normalization for overlay display [Deps: T018] [Output: failing state tests for rationale selection and debug-string cleanup]

### Implementation for User Story 3

- [X] T024 [US3] Rewrite `client/src/game/ui/SpeechBubble.ts` with Phaser graphics, wrapped text, truncation, and auto-fade behavior [Deps: T022] [Output: styled speech bubbles with rounded backgrounds, tails, and bounded text]
- [X] T025 [US3] Rewrite `client/src/game/ui/ThoughtCloud.ts` with distinct cloud-style visuals and bounded rationale text [Deps: T022] [Output: thought overlays visually distinct from speech bubbles]
- [X] T026 [US3] Update `client/src/game/ui/InteractionArc.ts` to render dashed animated conversation links instead of solid lines [Deps: T024, T025] [Output: warm animated interaction arcs for active conversations]
- [X] T027 [US3] Normalize overlay content selection and scene update flow in `client/src/game/scenes/WorldScene.ts` [Deps: T023, T024, T025, T026] [Output: the scene displays concise speech and thought text rather than raw debug strings]

**Checkpoint**: Conversations appear as styled speech bubbles, thoughts render as cloud overlays, and interaction arcs visibly connect active speakers.

---

## Phase 6: User Story 4 - Inspect an Agent Through a Polished Detail Panel (Priority: P4)

**Goal**: Selecting an agent reveals a dark-theme panel with needs bars, goal summary, recent decisions, and recent messages.

**Independent Test**: After several ticks, click an agent and confirm the side panel surfaces needs, active goal, recent decisions, and conversation history in an organized layout.

### Tests for User Story 4

- [X] T028 [P] [US4] Add selected-agent view-model tests in `client/tests/useSimulationState.test.ts` for ordered needs, decision-log limits, and recent conversation extraction [Deps: T018] [Output: failing state tests for panel-ready selected-agent data]
- [X] T029 [P] [US4] Add styled panel rendering coverage in `client/tests/agent-detail-panel.test.tsx` [Deps: T028] [Output: failing UI tests for needs bars, goal card, decision log, and conversation feed rendering]

### Implementation for User Story 4

- [X] T030 [US4] Rewrite `client/src/panels/AgentDetailPanel.tsx` with dark-theme header, colored needs bars, goal card, decision log, and conversation feed [Deps: T029] [Output: a structured side panel replacing the plain-text agent details]
- [X] T031 [US4] Tune selected-agent ordering, tick labels, and rationale excerpts in `client/src/panels/AgentDetailPanel.tsx` [Deps: T030] [Output: panel content remains readable and chronologically useful during live observation]

**Checkpoint**: Clicking an agent shows a polished research-friendly detail panel with colored bars and scrollable recent context instead of raw text blocks.

---

## Phase 7: User Story 5 - Watch Smooth Movement Instead of Teleporting (Priority: P5)

**Goal**: Agents move smoothly between authoritative positions with directional walk and idle states.

**Independent Test**: Run a scenario where an agent crosses multiple tiles and verify that movement appears continuous between ticks rather than snapping instantly.

### Tests for User Story 5

- [ ] T032 [P] [US5] Add lerp timing and clamp coverage in `client/tests/interpolation.test.ts` [Deps: T020] [Output: failing unit tests for time-based interpolation factor computation and snap thresholds]
- [ ] T033 [P] [US5] Extend `client/tests/useReplay.test.ts` to verify snapshot buffering and frame-to-frame interpolation timing assumptions used by the live renderer [Deps: T018] [Output: failing tests for previous/current snapshot shifting and tick interval fallback behavior]

### Implementation for User Story 5

- [ ] T034 [US5] Replace hardcoded interpolation with time-based lerp computation in `client/src/game/systems/Interpolation.ts` [Deps: T032] [Output: reusable interpolation helper that derives `t` from tick timestamps and interval estimates]
- [ ] T035 [US5] Shift snapshot buffering, per-frame rendering, and movement direction detection in `client/src/game/scenes/WorldScene.ts` [Deps: T033, T034] [Output: the world scene interpolates every frame between previous and current authoritative snapshots]
- [ ] T036 [US5] Update `client/src/game/sprites/AgentSprite.ts` to switch directional walk and idle animations from movement deltas [Deps: T019, T035] [Output: agent sprites animate correctly during movement and return to idle when interpolation completes]
- [ ] T037 [US5] Run live browser verification for multi-tile movement through `client/src/game/scenes/WorldScene.ts`, `client/src/game/systems/Interpolation.ts`, and `client/src/game/sprites/AgentSprite.ts` [Deps: T036] [Output: confirmed smooth movement with no teleporting between ticks]

**Checkpoint**: Agents now walk smoothly through the house with direction-aware animation instead of snapping tile-to-tile.

---

## Phase 8: User Story 6 - Experience Environmental Polish Without Losing Clarity (Priority: P6)

**Goal**: Time-of-day tinting, minimap accuracy, camera reset, and asset documentation make the world easier to follow without obscuring behavior.

**Independent Test**: Run through multiple time-of-day states and camera positions, then verify tint, minimap, and recentering all improve orientation while preserving readability.

### Tests for User Story 6

- [ ] T038 [P] [US6] Add tint mapping coverage in `client/tests/day-night.test.ts` [Deps: T011] [Output: failing tests for sunrise, noon, sunset, and midnight color/alpha mapping]
- [ ] T039 [P] [US6] Extend `client/tests/world-scene.test.ts` for minimap layout alignment and camera reset behavior [Deps: T014, T035] [Output: failing scene tests for minimap geometry and double-click recenter behavior]

### Implementation for User Story 6

- [ ] T040 [US6] Update `client/src/game/systems/DayNight.ts` with the final time-of-day tint mapping and blend behavior [Deps: T038] [Output: readable day/night overlay tuned for noon, sunrise, sunset, and midnight]
- [ ] T041 [US6] Rework minimap rendering and add double-click camera reset in `client/src/game/scenes/WorldScene.ts` [Deps: T039, T040] [Output: minimap reflects the real house layout and camera can reset to a predictable overview]
- [ ] T042 [US6] Finalize attribution coverage in `client/public/assets/ATTRIBUTION.md` for the shipped tileset and agent sprites [Deps: T005] [Output: complete asset license documentation aligned to the final visual files]
- [ ] T043 [US6] Run browser verification for tint, minimap, and recentering through `client/src/game/systems/DayNight.ts` and `client/src/game/scenes/WorldScene.ts` [Deps: T041, T042] [Output: confirmed environmental polish remains readable during live observation]

**Checkpoint**: The scene now has readable time-of-day tinting, an aligned minimap, predictable camera reset, and complete asset attribution.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full client-only visual fix end-to-end and capture final operator guidance.

- [ ] T044 [P] Run the full local embodied workflow using `maps/house.json`, `client/src/game/scenes/WorldScene.ts`, and `client/src/panels/AgentDetailPanel.tsx` from `init_db` through ten live ticks in the browser [Deps: T031, T037, T043] [Output: end-to-end smoke validation for the shipped visual experience]
- [ ] T045 [P] Verify existing embodied backend regression coverage still passes against `maps/house.json` and the shared spatial contracts [Deps: T006, T044] [Output: zero Python regressions from the visual-fix asset swap]
- [ ] T046 [P] Verify the Streamlit dashboard still behaves unchanged alongside the client fix using the existing dashboard workflow [Deps: T044] [Output: confirmed no dashboard regressions while the client visuals improve]
- [ ] T047 Update `specs/003-embodied-world-visual-fix/quickstart.md` with the final validated asset, run, and verification steps [Deps: T044, T045, T046] [Output: quickstart reflects the true shipped workflow and visual checks]
- [ ] T048 Mark completed tasks and add final verification notes in `specs/003-embodied-world-visual-fix/tasks.md` [Deps: T047] [Output: execution tracker and closeout notes kept accurate during implementation]

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: starts immediately and must finish before renderer work.
- **Foundational (Phase 2)**: depends on Setup and blocks all user stories.
- **User Stories (Phases 3-8)**: depend on Foundational rendering being complete.
- **Polish (Phase 9)**: depends on all desired user stories being complete.

### User Story Dependency Graph

- **US1 (P1)** depends on Setup + Foundational map rendering.
- **US2 (P2)** depends on US1’s real tilemap and asset-loading path.
- **US3 (P3)** depends on US2’s live sprite placement and world-scene update flow.
- **US4 (P4)** depends on selected-agent data already being exposed during US2/US3.
- **US5 (P5)** depends on US2 sprite rendering and should be pulled onto the critical path immediately after character rendering.
- **US6 (P6)** depends on the stable scene and movement foundations from US1, US2, and US5.

### Within Each User Story

- validate contracts or test expectations first
- update renderer/state plumbing before polish behavior
- finish the story-specific implementation before running the story checkpoint
- keep the client read-only with no simulation logic moved out of the backend

### Parallel Opportunities

- Phase 1 design/asset tasks marked `[P]` can run in parallel where file ownership differs.
- Foundational test tasks `T007-T008` can run in parallel.
- US2 tests `T017-T018` can run in parallel.
- US3 tests `T022-T023` can run in parallel.
- US4 tests `T028-T029` can run in parallel.
- US5 tests `T032-T033` can run in parallel.
- US6 tests `T038-T039` can run in parallel.

---

## Parallel Example: User Story 2

```bash
Task: "Add sprite identity and tile-to-pixel mapping tests in client/tests/agent-sprite.test.ts"
Task: "Extend client/tests/useSimulationState.test.ts to verify stable agent ordering and render-state mapping"
```

## Parallel Example: User Story 3

```bash
Task: "Add overlay text formatting and truncation tests in client/tests/overlay-ui.test.ts"
Task: "Extend client/tests/useSimulationState.test.ts to validate speech and thought payload normalization"
```

## Parallel Example: User Story 6

```bash
Task: "Add tint mapping coverage in client/tests/day-night.test.ts"
Task: "Extend client/tests/world-scene.test.ts for minimap layout alignment and camera reset behavior"
```

---

## Critical Path

1. `T001` -> `T003` -> `T004` -> `T006`
2. `T009` -> `T010` -> `T011` -> `T012`
3. `T019` -> `T020` -> `T021`
4. `T034` -> `T035` -> `T036` -> `T037`
5. `T040` -> `T041` -> `T043` -> `T044` -> `T047`

The minimum execution sequence for a believable embodied viewer is still:

```text
Phase 1 (assets) -> Phase 2 (tilemap rendering) -> Phase 4 (characters) -> Phase 7 (smooth movement)
```

After smooth movement is stable, overlay polish, side-panel polish, and environmental polish can proceed in parallel before the final smoke pass.

---

## Defer For Later

- new backend simulation logic or decision-engine changes
- new WebSocket message types or REST endpoints
- Python `app/` changes beyond a truly minimal parser-compatibility tweak if the final Tiled export requires it
- Streamlit dashboard modifications
- procedural map generation
- outdoor or village expansion
- 3D rendering, physics, or narrative director features
- auth, cloud services, multiplayer, or new npm package dependencies

---

## Implementation Strategy

### MVP First

1. Finish all Phase 1 asset and map-design work.
2. Complete Phase 2 so the real house renders in Phaser.
3. Deliver US2 characters on the real map.
4. Pull US5 interpolation onto the critical path so movement feels embodied.
5. Validate the browser before layering more UI polish.

### Incremental Delivery

1. Assets and Tiled map
2. Real tilemap rendering
3. Character sprites
4. Smooth movement
5. Overlays and side panel
6. Day/night, minimap, and smoke validation

### Single-Developer Agent-Assisted Flow

1. One pass handles asset acquisition and Tiled export.
2. One pass handles Phaser loader and tilemap scene work.
3. One pass handles sprite/interpolation logic.
4. One pass handles overlays, side panel, and final polish.

---

## Notes

- `[P]` tasks are only marked parallel when they do not edit the same files.
- The task list intentionally keeps asset acquisition first because every downstream fix depends on real PNG and map files existing.
- The client remains read-only throughout implementation.
- Reject changes that move pathfinding, state mutation, or decision logic into the browser.
