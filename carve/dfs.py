from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tiles import BaseTile
    from dirs import Direction
    from amazeing import Maze
from dirs import DIRS
from .utils import carvable, carve
from .wilson import braid


def dfs(maze: Maze, start: BaseTile, loop_chance: float = 0.0) -> None:
    """Carve a maze in the region reachable from `start` (recursive backtracker).
    loop_chance == 0.0 -> perfect maze.
    loop_chance  > 0.0 -> perfect maze, then braided like in wilson().
    """
    rng = maze._rng
    cells = maze.components[maze.component_of[start]]

    start.visited = True
    stack: list[BaseTile] = [start]

    while stack:
        current = stack[-1]

        # neighbours is a dict {direction: tile}: iterate over the DIRECTIONS,
        # because carve() needs the direction, not only the tile.
        options: list[Direction] = []
        for d in DIRS:
            n = current.neighbours[d]
            if carvable(n) and not n.visited:
                options.append(d)

        if not options:
            stack.pop()                 # dead end -> backtrack
            continue

        d = rng.choice(options)         # choose among VALID directions only
        nxt = current.neighbours[d]
        assert nxt is not None
        carve(current, d)               # opens the wall on both sides
        nxt.visited = True
        stack.append(nxt)

    if loop_chance > 0.0:
        braid(rng, cells, loop_chance)
