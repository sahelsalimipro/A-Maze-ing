from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amazeing import Maze
    from tiles import BaseTile
from errors import ConfigErr

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