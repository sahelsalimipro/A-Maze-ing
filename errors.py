from __future__ import annotations
from typing import TYPE_CHECKING
import os

import globals
if TYPE_CHECKING:
    from regions import Region
    from config import Settings


class ConfigErr(Exception):

    """Invalid or missing configuration. Stops the program at startup."""
    def __init__(self, msg: str = "", config: object = None) -> None:
        """Create the error. Without msg, guess the cause: missing .env,
        no environment variables or empty config.
        """
        if not msg:
            if not os.path.exists(".env"):
                msg = "No .env file detected"
            elif not os.environ:
                msg = "Error reading env variables: none detected"
            elif not config:
                msg = "Error empty config"
            else:
                msg = "Unknown config error"
        super().__init__(msg)
        self.config = config


def assert_rendering_dimensions(regions: dict[str, Region]) -> None:
    """Check that the middle regions line up (debug only).

    Raises:
        ValueError: if no middle region is defined.
        AssertionError: if their widths or side heights differ.
    """
    mid_regions = [
        regions[name] for name in globals.MID_REGION_ORDER if name in regions
    ]

    if not mid_regions:
        raise ValueError(
            "no middle regions defined (padd-top/banner/maze/padd-bottom)"
        )

    expected_w = mid_regions[0].width
    for r in mid_regions:
        assert r.width == expected_w, (
            f"uneven width for middle regions "
            f"(expected {expected_w}, got {r.width})"
        )

    expected_h = sum(r.height for r in mid_regions)
    for side in ("padd-left", "padd-right"):
        if side not in regions:
            raise ValueError(f"missing required region: {side}")
        assert regions[side].height == expected_h, (
            f"{side} height err (expected {expected_h}, "
            f"got {regions[side].height})"
        )


def validate(config: Settings) -> None:

    """Check the settings that depend on each other.

    Raises:
        ConfigErr: if the maze has fewer than 2 cells, or the carver
            or solver is unknown.
    """
    def _is_below(val, below) -> bool:
        """True if val < below."""
        return val < below

    def _is_above(val, above) -> bool:
        """True if val > above."""
        return val > above

    maze_w, maze_h = config["WIDTH"], config["HEIGHT"]

    # Entry and exit must be two different cells
    if _is_below(maze_w, 1) or _is_below(maze_h, 1) or maze_w * maze_h < 2:
        raise ConfigErr(
            f"Maze dimensions specified {maze_w}x{maze_h} too small: "
            "the maze needs at least 2 cells"
        )
#     tile_ratio = config.get("TILE_RATIO", (0, 0))
#     if _is_below(tile_ratio[0], 1) or _is_below(tile_ratio[1], 1):
#         raise ConfigErr(
#             f"Tile ratio specified {tile_ratio[0]},{tile_ratio[1]}\
#  too small, min 1,1"
#         )
    carver = config.get("CARVER_ALGO", str()).lower()
    solver = config.get("SOLVER_ALGO", str()).lower()

    if carver != "dfs" and carver != "wilson":
        raise ConfigErr(
            f"Invalid carver provided: {carver!r}. "
            "Valid carvers are: 'dfs', 'wilson'."
        )

    if solver != "bfs" and solver != "astar":
        raise ConfigErr(
            f"Invalid solver provided: {solver!r}. "
            "Valid solvers are: 'bfs', 'astar'."
        )

    # Theme name: validated by themes_loader.activate_theme(), which runs
    # before this and raises ConfigErr for an unknown or broken theme.
