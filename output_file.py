"""Write a maze to a text file using the subject's hexadecimal format."""
from __future__ import annotations
from typing import TYPE_CHECKING

from dirs import DELTAS, Direction
from solvers import bfs

if TYPE_CHECKING:
    from amazeing import Maze
    from tiles import BaseTile


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
