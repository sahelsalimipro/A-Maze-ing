from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from tiles import BaseTile
    from dirs import Direction
    from amazeing import Maze
from dirs import DIRS
from .utils import carvable, carve, reachable


def wilson(maze: Maze, start: BaseTile, loop_chance: float = 0.0) -> None:
    """Carve a maze in the region reachable from `start`.
    loop_chance == 0.0 -> perfect maze.
    loop_chance  > 0.0 -> perfect maze, then that fraction of dead ends
                          get an extra wall opened (imperfect).
    """
    rng = maze._rng
    cells = reachable(start)

    in_maze: set[BaseTile] = {start}   # the root; any root gives an unbiased result

    # Shuffling once, then walking the list in order, is equivalent to
    # repeatedly picking a random cell that is not yet in the maze.
    order: list[BaseTile] = [c for c in cells if c is not start]
    rng.shuffle(order)

    for begin in order:
        if begin in in_maze:
            continue

        # Phase 1: random walk until we hit the maze.
        # Overwriting exit_dir on revisits is what "erases" loops.
        exit_dir: dict[BaseTile, Direction] = {}
        cur = begin
        while cur not in in_maze:
            options: list[Direction] = [
                d for d in DIRS
                if carvable(cur.neighbours[d])
            ]
            d = rng.choice(options)
            exit_dir[cur] = d
            nxt = cur.neighbours[d]
            assert nxt is not None
            cur = nxt

        # Phase 2: retrace the loop-free path and carve it.
        cur = begin
        while cur not in in_maze:
            d = exit_dir[cur]
            nxt = cur.neighbours[d]
            assert nxt is not None
            carve(cur, d)
            in_maze.add(cur)
            cur = nxt

    if loop_chance > 0.0:
        braid(rng, cells, loop_chance)


def braid(rng: random.Random, cells: list[BaseTile], p: float) -> None:
    for t in cells:
        if t.wallscount != 3 or rng.random() > p:
            continue

        closed: list[Direction] = [
            d for d in DIRS
            if t.walls[d] and carvable(t.neighbours[d])
        ]
        if not closed:          # dead end walled in by limits/logo
            continue

        # prefer linking two dead ends together
        pref: list[Direction] = []
        for d in closed:
            n = t.neighbours[d]
            if n is not None and n.wallscount == 3:
                pref.append(d)

        carve(t, rng.choice(pref or closed))
