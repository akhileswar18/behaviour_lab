# Sprite Asset Contract

## Purpose

This contract defines the spritesheet format and loading expectations for embodied-world agent
character visuals.

## File Locations

- `client/public/assets/tilesets/agents/agent_1.png`
- `client/public/assets/tilesets/agents/agent_2.png`
- `client/public/assets/tilesets/agents/agent_3.png`

## Naming Convention

- Texture keys in Phaser map directly to the file stem:
  - `agent_1`
  - `agent_2`
  - `agent_3`
- Agent identity mapping should be deterministic so the same agent reuses the same visual in a
  session.

## Frame Format

| Property | Required Value |
|----------|----------------|
| `frameWidth` | `16` |
| `frameHeight` | `16` |
| `columns` | `4` |
| `rows` | `4` |
| `framesPerDirection` | `4` |

## Layout Convention

Rows must map to directions in this exact order:

| Row | Direction |
|-----|-----------|
| `0` | Down |
| `1` | Left |
| `2` | Right |
| `3` | Up |

Columns represent the walk cycle frames from left to right.

## Animation Expectations

Required animation keys:

- `walk_down`
- `walk_left`
- `walk_right`
- `walk_up`
- `idle`

Animation rules:

- walk animations use the 4 frames in the row for the matching direction
- `idle` uses the first frame from the down-facing row unless a future enhancement adds a
  dedicated idle strip
- walk animations should play at approximately 8 fps
- sprites render at 3x display scale for a visible on-screen size of 48x48 pixels

## Loader Expectations

`Preloader.ts` must:

- call `this.load.spritesheet(...)` for each agent asset
- supply `frameWidth: 16` and `frameHeight: 16`

`AgentSprite.ts` must:

- create and reuse the required animation keys
- switch animation according to movement direction
- preserve `setInteractive()` selection behavior on the rendered sprite

## Fallback Rules

- If a specific spritesheet is missing, the client may fall back to a colored marker with the
  agent's initial while preserving selection and labels.
- If only some agent sprites are available, mixed-mode rendering is acceptable as a degraded
  fallback.
- Missing sprite assets must not crash the scene or block live observation.
