import { describe, expect, it } from "vitest";

import {
  AGENT_FRAME_SIZE,
  AGENT_SPRITE_KEYS,
  AGENT_SPRITE_SCALE,
  WORLD_TILE_SIZE,
  tileToWorldPosition,
} from "../src/game/sprites/AgentSprite";

describe("AgentSprite helpers", () => {
  it("uses the shipped sprite keys and 3x scale for 16x16 characters", () => {
    expect(AGENT_SPRITE_KEYS).toEqual(["agent_1", "agent_2", "agent_3"]);
    expect(AGENT_FRAME_SIZE).toBe(16);
    expect(AGENT_SPRITE_SCALE).toBe(3);
    expect(WORLD_TILE_SIZE).toBe(48);
  });

  it("maps tile coordinates to the center of each rendered tile", () => {
    expect(tileToWorldPosition({ tile_x: 0, tile_y: 0 })).toEqual({ x: 24, y: 24 });
    expect(tileToWorldPosition({ tile_x: 5, tile_y: 3 })).toEqual({ x: 264, y: 168 });
    expect(tileToWorldPosition({ tile_x: 8, tile_y: 9 })).toEqual({ x: 408, y: 456 });
  });
});
