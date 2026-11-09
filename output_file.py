"""Write a maze to a text file using the subject's hexadecimal format."""
from __future__ import annotations
from typing import TYPE_CHECKING

from dirs import DELTAS, Direction
from solvers import bfs

if TYPE_CHECKING:
    from amazeing import Maze
    from tiles import BaseTile



# One bit per wall: N=1, E=2, S=4, W=8 (subject, section 4.5)
WALL_BITS: dict[Direction, int] = {"N": 1, "E": 2, "S": 4, "W": 8}

# (dx, dy) -> letter, the reverse of DELTAS: (0, -1) -> "N", ...
STEP_TO_DIR: dict[tuple[int, int], Direction] = {
    delta: d for d, delta in DELTAS.items()
}


def tile_to_hex(tile: BaseTile) -> str:
    """Return one hex digit: the sum of the bits of the closed walls."""
    value = 0
    for d, bit in WALL_BITS.items():
        if tile.walls[d]:
            value += bit
    return format(value, "X")


def path_to_letters(path: list[BaseTile]) -> str:
    """Turn a list of tiles into moves, e.g. [A, B, C] -> "ES"."""
    letters: list[str] = []
    for a, b in zip(path, path[1:]):
        letters.append(STEP_TO_DIR[(b.x - a.x, b.y - a.y)])
    return "".join(letters)


def write_output(maze: Maze, filename: str) -> None:
    """Write the maze, entry, exit and shortest path to `filename`.

    Raises:
        ValueError: if there is no path between entry and exit.
        OSError: if the file cannot be written.
    """
    lines: list[str] = []

    # 1. the grid, without the Limit ring around it
    for row in maze.grid[1:-1]:
        lines.append("".join(tile_to_hex(t) for t in row[1:-1]))

    # 2. empty line
    lines.append("")

    # 3. entry and exit, in config coordinates (-1 for the Limit ring)
    start, goal = maze._start, maze._goal
    lines.append(f"{start.x - 1},{start.y - 1}")
    lines.append(f"{goal.x - 1},{goal.y - 1}")

    # 4. shortest path as letters
    path = bfs(start, goal)
    if path is None:
        raise ValueError("No path between entry and exit")
    lines.append(path_to_letters(path))

    with open(filename, "w") as f:
        f.write("\n".join(lines) + "\n")
