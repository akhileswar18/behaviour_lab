from app.simulation.pathfinding import astar_path


def test_astar_path_finds_simple_route() -> None:
    grid = [
        [False, False, False],
        [True, True, False],
        [False, False, False],
    ]

    path = astar_path(grid, (0, 0), (2, 2))

    assert path[0] == (0, 0)
    assert path[-1] == (2, 2)
    assert len(path) >= 4


def test_astar_path_returns_empty_for_blocked_goal() -> None:
    grid = [
        [False, False],
        [False, True],
    ]

    assert astar_path(grid, (0, 0), (1, 1)) == []
