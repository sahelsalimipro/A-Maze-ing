from __future__ import annotations
from typing import TYPE_CHECKING

import globals
from maze import Maze
from output_file import write_output
from regions import Region
from dimensions import resolve_dimensions
from themes_loader import activate_theme, load_theme

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
    globals.MAZE = maze


def build_regions() -> None:
    """(Re)computes the layout from the config and refills globals.REGIONS
    *in place*: run() holds a reference to that same dict."""
    rects = resolve_dimensions(globals.CONFIG)
    globals.REGIONS.clear()
    globals.REGIONS.update(
        {name: Region(name, rects[name]) for name in globals.REGIONS_NAMES}
    )


def switch_theme() -> None:
    """Activates the theme the config asks for, then rebuilds the layout
    and the drawers. The maze itself is kept."""
    globals.THEME_MODULE = activate_theme(globals.CONFIG)
    build_regions()
    attach_drawers(globals.MAZE)
