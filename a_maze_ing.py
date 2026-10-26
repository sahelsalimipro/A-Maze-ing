from typing import Any, cast
import sys

from render import clear_console, render, run
from logger import setup_logging
from config import load_config
from errors import ConfigErr, assert_rendering_dimensions
from regions import Region
from dimensions import resolve_dimensions
from amazeing import Maze
from themes_loader import load_theme


if __name__ == "__main__":
    setup_logging()
    config: dict[str, Any] | None = None
    try:
        config = load_config()
    except ConfigErr as e:
        print(f"ABORTING EARLY Error during configuration:\n{e}")
        sys.exit(1)

    import globals  # noqa: E402
    assert config is not None
    globals.CONFIG = config

    clear_console()

    # Ruling to ensure dimensions of each region. 1 region = 1 drawer
    rects = resolve_dimensions(config)
    regions: dict[str, Region] = {
        name: Region(name, rects[name]) for name in globals.REGIONS_NAMES
    }

    # Creating the maze
    maze = Maze(dimensions=(config["MAZE_WIDTH"],
                config["MAZE_HEIGHT"]), seed=42)

    # Prepares the drawers, responsible for rendering
    drawers = load_theme(cast(str, config.get("THEME_NAME")), config, maze)

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

    except KeyboardInterrupt as e:
        clear_console()
        print(f"\n\n{'Goodbye user!':^24}\n\n")

    except Exception as e:
        print(f"RuntimeError: {e}")
