from __future__ import annotations
from typing import TYPE_CHECKING, Any
import os

from regions import Region
from globals import MID_REGION_ORDER
if TYPE_CHECKING:
    from tiles import BaseTile


class InvalidTileErr(ValueError):

    def __init__(
        self,
        tile: BaseTile,
        msg: str = "Invalid tile",
        *args: object
    ) -> None:
        self.tile = tile
        self.msg = msg
        self.full_msg = f"{msg}\nInfo: {self.tile}"
        super().__init__(self.full_msg, *args)


class ConfigErr(Exception):

    def __init__(self, msg: str = "", config: object = None) -> None:
        if not msg:
            if not os.path.exists(".env"):
                msg = "No .env file detected"
            elif not os.environ:
                msg = "Error reading env variables: none detected"
            elif not config:
                msg = "Error empty config"
            else:
                msg = "Unknown config error"
        super().__init__(msg, config)


def assert_rendering_dimensions(regions: dict[str, Region]) -> None:
    mid_regions = [
        regions[name] for name in MID_REGION_ORDER if name in regions
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


def validate(config: dict[str, Any]) -> None:

    def _is_below(val, below) -> bool:
        return val < below

    def _is_above(val, above) -> bool:
        return val > above

    maze_w, maze_h = config.get("MAZE_WIDTH"), config.get("MAZE_HEIGHT")

    if _is_below(maze_w, 9) or _is_below(maze_h, 7):
        raise ConfigErr(
            f"Maze dimensions specified {maze_w}x{maze_h} too small, min 9x7"
        )
#     tile_ratio = config.get("TILE_RATIO", (0, 0))
#     if _is_below(tile_ratio[0], 1) or _is_below(tile_ratio[1], 1):
#         raise ConfigErr(
#             f"Tile ratio specified {tile_ratio[0]},{tile_ratio[1]}\
#  too small, min 1,1"
#         )
    # TODO validate theme name.
