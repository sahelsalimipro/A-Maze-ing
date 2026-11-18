import sys
from types import ModuleType

import globals
from logger import setup_logging
from errors import ConfigErr, assert_rendering_dimensions, validate
from config import load_config, Settings
from app import build_maze, attach_drawers, build_regions
from themes_loader import activate_theme
from render import run

if __name__ == "__main__":
    config: Settings
    module: ModuleType

    setup_logging()
    try:
        config = load_config()
        module = activate_theme(config)
        validate(config)
        globals.CONFIG = config

    except ConfigErr as e:
        print(f"ABORTING EARLY Error during configuration:\n{e}")
        sys.exit(1)

    # Ruling to ensure dimensions of each region. 1 region = 1 drawer
    globals.THEME_MODULE = module
    build_regions()
    regions = globals.REGIONS

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
