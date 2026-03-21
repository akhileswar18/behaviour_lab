import { describe, expect, it } from "vitest";

import {
  DEFAULT_TICK_INTERVAL_MS,
  computeInterpolationFactor,
  estimateTickIntervalMs,
  interpolatePosition,
} from "../src/game/systems/Interpolation";

describe("Interpolation helpers", () => {
  it("computes a clamped interpolation factor from tick timing", () => {
    expect(
      computeInterpolationFactor({
        lastTickTimestamp: 1_000,
        now: 1_500,
        tickIntervalMs: 2_000,
      }),
    ).toBe(0.25);
    expect(
      computeInterpolationFactor({
        lastTickTimestamp: 1_000,
        now: 3_500,
        tickIntervalMs: 2_000,
      }),
    ).toBe(1);
    expect(
      computeInterpolationFactor({
        lastTickTimestamp: 2_000,
        now: 1_000,
        tickIntervalMs: 2_000,
      }),
    ).toBe(0);
  });

  it("falls back to immediate snap when timing data is missing or invalid", () => {
    expect(
      computeInterpolationFactor({
        lastTickTimestamp: null,
        now: 1_500,
        tickIntervalMs: 2_000,
      }),
    ).toBe(1);
    expect(
      computeInterpolationFactor({
        lastTickTimestamp: 1_000,
        now: 1_500,
        tickIntervalMs: 0,
      }),
    ).toBe(1);
  });

  it("estimates tick interval from local timing before falling back", () => {
    expect(
      estimateTickIntervalMs({
        previousTickTimestamp: 1_000,
        lastTickTimestamp: 3_000,
      }),
    ).toBe(2_000);
    expect(
      estimateTickIntervalMs({
        previousTickTimestamp: null,
        lastTickTimestamp: 3_000,
      }),
    ).toBe(DEFAULT_TICK_INTERVAL_MS);
  });

  it("interpolates between previous and current tile positions", () => {
    const previous = {
      agent_id: "a-1",
      name: "Cyra",
      position: { tile_x: 2, tile_y: 3 },
      mood: "calm",
      action: "move",
      needs: { hunger: 0.2, safety_need: 0.4, social_need: 0.3 },
      recent_decisions: [],
    };
    const current = {
      ...previous,
      position: { tile_x: 6, tile_y: 3 },
    };
    expect(interpolatePosition(previous, current, 0.5)).toEqual({
      tile_x: 4,
      tile_y: 3,
      subtile_progress: 0.5,
    });
  });
});
