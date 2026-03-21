import type { AgentSnapshot, TilePosition } from "../../types/world";

export const DEFAULT_TICK_INTERVAL_MS = 2_000;

export interface InterpolationFactorInput {
  lastTickTimestamp: number | null;
  now: number;
  tickIntervalMs: number;
}

export interface TickIntervalEstimateInput {
  previousTickTimestamp: number | null;
  lastTickTimestamp: number | null;
  fallbackTickIntervalMs?: number;
}

export function estimateTickIntervalMs({
  previousTickTimestamp,
  lastTickTimestamp,
  fallbackTickIntervalMs = DEFAULT_TICK_INTERVAL_MS,
}: TickIntervalEstimateInput): number {
  if (previousTickTimestamp === null || lastTickTimestamp === null) {
    return fallbackTickIntervalMs;
  }
  const interval = lastTickTimestamp - previousTickTimestamp;
  return interval > 0 ? interval : fallbackTickIntervalMs;
}

export function computeInterpolationFactor({
  lastTickTimestamp,
  now,
  tickIntervalMs,
}: InterpolationFactorInput): number {
  if (lastTickTimestamp === null || tickIntervalMs <= 0) {
    return 1;
  }
  return Math.max(0, Math.min(1, (now - lastTickTimestamp) / tickIntervalMs));
}

export function interpolatePosition(
  previous: AgentSnapshot | undefined,
  current: AgentSnapshot,
  alpha: number,
): TilePosition {
  const end = current.position ?? { tile_x: 0, tile_y: 0 };
  const start = previous?.position ?? end;
  return {
    tile_x: start.tile_x + (end.tile_x - start.tile_x) * alpha,
    tile_y: start.tile_y + (end.tile_y - start.tile_y) * alpha,
    subtile_progress: alpha,
  };
}
