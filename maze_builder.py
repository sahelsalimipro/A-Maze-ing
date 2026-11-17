from __future__ import annotations
from typing import TYPE_CHECKING

import globals
from maze import Maze
from output_file import write_output
from themes_loader import load_theme

if TYPE_CHECKING:
    from config import Settings


def build_maze(config: Settings) -> Maze:
    """Carves a maze from the config, solves it and writes the output file.
    Raises OSError/ValueError if the output file can't be written."""
    maze = Maze(
        config["MAZE_WIDTH"],
        config["MAZE_HEIGHT"],
        config["SEED"],
        config["PERFECT"],
        config["ENTRY"],
        config["EXIT"],
        config["CARVER_ALGO"],
        config["SOLVER_ALGO"]
    )
    # Always solved; the maze drawer shows the path only if SOLVED is on
    maze.resolve()
    write_output(maze, config["OUTPUT_FILE"])
    return maze


def attach_drawers(maze: Maze) -> None:
    """Builds the current theme's drawers for `maze` and attaches them to
    the regions. Takes effect on the next full redraw."""
    drawers = load_theme(globals.THEME_MODULE, globals.CONFIG, maze)
    for name, region in globals.REGIONS.items():
        region.attach(drawers[name])
