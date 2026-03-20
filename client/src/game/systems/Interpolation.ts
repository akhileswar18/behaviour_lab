import type { AgentSnapshot, TilePosition } from "../../types/world";

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
