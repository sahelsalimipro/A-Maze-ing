import sys
from types import ModuleType

import globals
from logger import setup_logging
from errors import ConfigErr, assert_rendering_dimensions, validate
from regions import Region
from config import load_config, Settings
from dimensions import resolve_dimensions
from maze_builder import build_maze, attach_drawers
from themes_loader import load_theme_module
from render import run

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


    # Ruling to ensure dimensions of each region. 1 region = 1 drawer
    rects = resolve_dimensions(config)
    regions: dict[str, Region] = {
        name: Region(name, rects[name]) for name in globals.REGIONS_NAMES
    }

    globals.THEME_MODULE = module
    globals.REGIONS = regions

    # Creating the maze (solved + written to the output file)
    try:
        maze = build_maze(config)
    except (OSError, ValueError) as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

    try:
        if __debug__:
            assert_rendering_dimensions(regions)

        # Prepares the drawers, responsible for rendering
        attach_drawers(maze)

        run(regions)

    except KeyboardInterrupt:
        print(f"\n\n{'Goodbye user!':^24}\n\n")

    except Exception as e:
        print(f"RuntimeError: {e}")
