from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amazeing import Maze
    from tiles import BaseTile
from errors import ConfigErr
from .utils import reachable, carvable


def validate_endpoints(entry: tuple[int, int], exit: tuple[int, int], maze: Maze) -> tuple[tuple[int, int], tuple[int, int]]:
    def _is_below(val: int, below: int) -> bool:
        return val < below

    def _is_above(val: int, above: int) -> bool:
        return val > above

    def _clamp(min: int, val: int, max: int) -> bool:
        return _is_above(val, min) and _is_below(val, max)

    maze_w, maze_h = maze.dimensions

    if not _clamp(-1, entry[0], maze_w + 1):
        raise ConfigErr(f"Invalid ENTRY x coordinate {entry[0]!r}")
    if not _clamp(-1, entry[1], maze_h + 1):
        raise ConfigErr(f"Invalid ENTRY y coordinate {entry[1]!r}")

    if not _clamp(-1, exit[0], maze_w + 1):
        raise ConfigErr(f"Invalid EXIT x coordinate {exit[0]!r}")
    if not _clamp(-1, exit[1], maze_h + 1):
        raise ConfigErr(f"Invalid EXIT y coordinate {exit[1]!r}")

    # start (entry)
    s_col, s_row = entry[0] + 1, entry[1] + 1  # +1 for offset of Limit tiles
    if maze.grid[s_row][s_col].isLogo:
        raise ConfigErr(
            f"Requested ENTRY coordinates {entry[0], entry[1]!r} is on a logo tile"
        )

    # goal (exit)
    g_col, g_row = exit[0] + 1, exit[1] + 1  # +1 for offset of Limit tiles
    if maze.grid[g_row][g_col].isLogo:
        raise ConfigErr(
            f"Requested EXIT coordinates {exit[0], exit[1]!r} is on a logo tile"
        )

    return ((s_col, s_row), (g_col, g_row))


def pick_endpoints(maze: Maze,
                   start: tuple[int, int] | None,
                   goal: tuple[int, int] | None
                   ) -> tuple[BaseTile, BaseTile]:

    # if we were given coordinates, validate and return the corresponding tiles
    if start is not None and goal is not None:
        start, goal = validate_endpoints(start, goal, maze)
        return ( maze.grid[start[0]][start[1]],
                maze.grid[goal[0]][goal[1]] )

    # else, pick the endpoints automatically
    rng = maze._rng

    def on_border(t: BaseTile) -> bool:
        return t.x in (1, maze.width) or t.y in (1, maze.height)

    border = [t for row in maze.grid for t in row
              if carvable(t) and on_border(t)]
    if not border:
        raise ValueError("No valid border tile for the entry")

    entry = rng.choice(border)

    # The exit must be on the border AND in the same region as the entry
    region = set(reachable(entry))
    candidates = [t for t in border if t in region and t is not entry]
    if not candidates:
        raise ValueError("No valid exit reachable from the entry")

    exit_ = rng.choice(candidates)

    return entry, exit_
