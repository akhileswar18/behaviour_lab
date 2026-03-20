from __future__ import annotations

from heapq import heappop, heappush


def _neighbors(tile_x: int, tile_y: int) -> list[tuple[int, int]]:
    return [
        (tile_x + 1, tile_y),
        (tile_x - 1, tile_y),
        (tile_x, tile_y + 1),
        (tile_x, tile_y - 1),
    ]


def _heuristic(start: tuple[int, int], goal: tuple[int, int]) -> int:
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])


def _in_bounds(grid: list[list[bool]], tile_x: int, tile_y: int) -> bool:
    return 0 <= tile_y < len(grid) and 0 <= tile_x < len(grid[0])


def astar_path(
    collision_grid: list[list[bool]],
    start: tuple[int, int],
    goal: tuple[int, int],
) -> list[tuple[int, int]]:
    if not collision_grid:
        return []
    if start == goal:
        return [start]
    if not _in_bounds(collision_grid, *start) or not _in_bounds(collision_grid, *goal):
        return []
    if collision_grid[goal[1]][goal[0]]:
        return []

    frontier: list[tuple[int, tuple[int, int]]] = []
    heappush(frontier, (0, start))
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    cost_so_far: dict[tuple[int, int], int] = {start: 0}

    while frontier:
        _, current = heappop(frontier)
        if current == goal:
            break
        for neighbor in _neighbors(*current):
            if not _in_bounds(collision_grid, *neighbor):
                continue
            if collision_grid[neighbor[1]][neighbor[0]]:
                continue
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + _heuristic(neighbor, goal)
                heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    if goal not in came_from:
        return []

    current = goal
    path = [current]
    while current != start:
        parent = came_from[current]
        if parent is None:
            break
        current = parent
        path.append(current)
    path.reverse()
    return path
