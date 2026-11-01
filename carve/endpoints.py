from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amazeing import Maze
    from tiles import BaseTile
from errors import ConfigErr
from .utils import find_components, carvable


# def validate_endpoints(entry: tuple[int, int], exit: tuple[int, int], maze: Maze) -> tuple[tuple[int, int], tuple[int, int]]:
#     def _is_below(val: int, below: int) -> bool:
#         return val < below

#     def _is_above(val: int, above: int) -> bool:
#         return val > above

#     def _clamp(min: int, val: int, max: int) -> bool:
#         return _is_above(val, min) and _is_below(val, max)

#     maze_w, maze_h = maze.dimensions

#     if not _clamp(-1, entry[0], maze_w + 1):
#         raise ConfigErr(f"Invalid ENTRY x coordinate {entry[0]!r}")
#     if not _clamp(-1, entry[1], maze_h + 1):
#         raise ConfigErr(f"Invalid ENTRY y coordinate {entry[1]!r}")

#     if not _clamp(-1, exit[0], maze_w + 1):
#         raise ConfigErr(f"Invalid EXIT x coordinate {exit[0]!r}")
#     if not _clamp(-1, exit[1], maze_h + 1):
#         raise ConfigErr(f"Invalid EXIT y coordinate {exit[1]!r}")

#     # start (entry)
#     s_col, s_row = entry[0] + 1, entry[1] + 1  # +1 for offset of Limit tiles
#     if maze.grid[s_row][s_col].isLogo:
#         raise ConfigErr(
#             f"Requested ENTRY coordinates {entry[0], entry[1]!r} is on a logo tile"
#         )

#     # goal (exit)
#     g_col, g_row = exit[0] + 1, exit[1] + 1  # +1 for offset of Limit tiles
#     if maze.grid[g_row][g_col].isLogo:
#         raise ConfigErr(
#             f"Requested EXIT coordinates {exit[0], exit[1]!r} is on a logo tile"
#         )

#     return ((s_col, s_row), (g_col, g_row))


# def pick_endpoints(maze: Maze,
#                    start: tuple[int, int] | None,
#                    goal: tuple[int, int] | None
#                    ) -> tuple[BaseTile, BaseTile]:

#     # if we were given coordinates, validate and return the corresponding tiles
#     if start is not None and goal is not None:
#         start, goal = validate_endpoints(start, goal, maze)
#         return ( maze.grid[start[0]][start[1]],
#                 maze.grid[goal[0]][goal[1]] )

#     # else, pick the endpoints automatically
#     rng = maze._rng

#     def on_border(t: BaseTile) -> bool:
#         return t.x in (1, maze.width) or t.y in (1, maze.height)

#     border = [t for row in maze.grid for t in row
#               if carvable(t) and on_border(t)]
#     if not border:
#         raise ValueError("No valid border tile for the entry")

#     entry = rng.choice(border)

#     # The exit must be on the border AND in the same region as the entry
#     region = set(reachable(entry))
#     candidates = [t for t in border if t in region and t is not entry]
#     if not candidates:
#         raise ValueError("No valid exit reachable from the entry")

#     exit_ = rng.choice(candidates)

#     return entry, exit_

Coord = tuple[int, int]


def _hint(label: str) -> str:
    return f"Pick other coordinates, or set {label} to NONE to let the program choose it."

def _coord(t: BaseTile) -> Coord:
    """Returns grid -> config coordinates"""
    return (t.x - 1, t.y - 1)

def _on_border(maze: Maze, t: BaseTile) -> bool:
    return t.x in (1, maze.width) or t.y in (1, maze.height)

def _prefer_border(maze: Maze, tiles: list[BaseTile]) -> list[BaseTile]:
    return [t for t in tiles if _on_border(maze, t)] or tiles

def _resolve(maze: Maze, coord: Coord | None, label: str) -> BaseTile | None:
    """None stays None. Anything given is validated, never corrected."""
    if coord is None:
        return None
    x, y = coord
    if not (0 <= x < maze.width and 0 <= y < maze.height):
        raise ConfigErr(
            f"{label} {coord} is outside the maze "
            f"(x: 0-{maze.width - 1}, y: 0-{maze.height - 1}). {_hint(label)}"
        )
    tile = maze.grid[y + 1][x + 1]          # +1: Limit ring; grid is [row][col]
    if tile.isLogo:
        raise ConfigErr(f"{label} {coord} is on a logo tile. {_hint(label)}")
    return tile


def _pick_near(maze: Maze, anchor: BaseTile, label: str) -> BaseTile:
    """Pick the missing endpoint in the anchor's component (border preferred)."""
    others = [t for t in maze.components[maze.component_of[anchor]] if t is not anchor]
    if not others:
        raise ConfigErr(
            f"{label} {_coord(anchor)} is isolated by the logo: no other tile "
            f"can be reached. {_hint(label)}"
        )
    return maze._rng.choice(_prefer_border(maze, others))


def pick_endpoints(
    maze: Maze, entry: Coord | None, exit_: Coord | None
) -> tuple[BaseTile, BaseTile]:
    """Returns (start, goal). Given coordinates are validated, never corrected."""
    start = _resolve(maze, entry, "ENTRY")
    goal = _resolve(maze, exit_, "EXIT")

    if start is not None and goal is not None:
        if start is goal:
            raise ConfigErr(
                f"ENTRY and EXIT are the same tile {_coord(start)}. "
                f"Pick different coordinates, or set one of them to NONE."
            )
        if maze.component_of[start] != maze.component_of[goal]:
            raise ConfigErr(
                f"ENTRY {_coord(start)} and EXIT {_coord(goal)} are not connected "
                f"(the logo separates them). Move one, or set one of them to NONE."
            )
        return start, goal

    if start is not None:                    # EXIT missing
        return start, _pick_near(maze, start, "ENTRY")

    if goal is not None:                     # ENTRY missing
        return _pick_near(maze, goal, "EXIT"), goal

    # Neither given: start in the biggest component so we never land in a pocket
    main = max(maze.components, key=len)     # ties: first one, deterministic
    start = maze._rng.choice(_prefer_border(maze, main))
    return start, _pick_near(maze, start, "ENTRY")