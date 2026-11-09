from typing import cast
import sys
from types import ModuleType

import globals
from logger import setup_logging
from errors import ConfigErr, assert_rendering_dimensions, validate
from regions import Region
from config import load_config, Settings
from dimensions import resolve_dimensions
from amazeing import Maze, GenInfos
from themes_loader import load_theme_module, load_theme
from render import clear_console, render, run
from output_file import write_output

if __name__ == "__main__":
    config: Settings
    module: ModuleType

    setup_logging()
    try:
        config = load_config()
        theme_name = config["THEME_NAME"] if config["THEME_ON"] else "default"
        module = load_theme_module(theme_name)
        overrides = getattr(module, "OVERRIDES", {})
        config.apply_theme(overrides)
        validate(config)
        globals.CONFIG = config

    except ConfigErr as e:
        print(f"ABORTING EARLY Error during configuration:\n{e}")
        sys.exit(1)


    clear_console()

    # Ruling to ensure dimensions of each region. 1 region = 1 drawer
    rects = resolve_dimensions(config)
    regions: dict[str, Region] = {
        name: Region(name, rects[name]) for name in globals.REGIONS_NAMES
    }

    # Creating the maze
    gen_infos = GenInfos(config["SEED"], 0 if config["PERFECT"] else 8)
    maze = Maze((config["MAZE_WIDTH"], config["MAZE_HEIGHT"]), gen_infos)
    try:
        write_output(maze, config["OUTPUT_FILE"])
    except (OSError, ValueError) as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

    # Prepares the drawers, responsible for rendering
    drawers = load_theme(module, config, maze)

    try:
        if __debug__:
            assert_rendering_dimensions(regions)

        if config.get("SOLVED", False):
            maze.resolve()

        for name, region in regions.items():
            region.attach(drawers[name])
            region.fill_buffer(config)
        render(regions)
        run(list(regions.values()))

    except KeyboardInterrupt:
        clear_console()
        print(f"\n\n{'Goodbye user!':^24}\n\n")

    except Exception as e:
        print(f"RuntimeError: {e}")
