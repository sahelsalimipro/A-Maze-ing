from typing import NamedTuple, Any

from drawers import _total_buf
from menu import compute_menu_layout, COMMANDS
import globals


class Rect(NamedTuple):
    x: int
    y: int
    w: int
    h: int


def _split_horizontal_space(
    maze_width: int, left: int, right: int, columns: int, center: bool
) -> tuple[int, int, int, int]:
    """Returns (padd_left, padd_right, extra_left, extra_right)."""
    free: int = columns - maze_width

    if center:
        target_left = free // 2
        target_right = free - target_left
    elif left + right > free:                   # Not enough room: cut, keep ratio
        target_left = free * left // (left + right)
        target_right = free - target_left
    else:                                       # Fits: keep paddings, spare goes right
        target_left = left
        target_right = free - left

    padd_left = min(left, target_left)
    padd_right = min(right, target_right)
    return (
        padd_left,
        padd_right,
        target_left - padd_left,
        target_right - padd_right,
    )


def resolve_dimensions(config: dict[str, Any]) -> dict[str, Rect]:
    ratio_x, ratio_y = config["TILE_RATIO"]
    ct_cols = config["MAZE_WIDTH"]   # doesn't include Limit border tiles
    ct_rows = config["MAZE_HEIGHT"]

    maze_width: int = _total_buf(ct_cols, ratio_x)
    maze_height: int = _total_buf(ct_rows, ratio_y)

    # Sets this computed value for later
    globals.MID_WIDTH = maze_width

    total_height: int = (
        config["TOP_PADDING"] + config["BOT_PADDING"]
        + maze_height + globals.BANNER_HEIGHT
    )

    padd_l, padd_r, xt_l, xt_r = _split_horizontal_space(
        maze_width,
        config["LEFT_PADDING"],
        config["RIGHT_PADDING"],
        globals.TERMINAL_SIZE.columns,
        config.get("CENTER_MAZE", False),
    )

    x_mid = xt_l + padd_l                       # left edge of the centre column
    x_right = x_mid + maze_width                # where padd-right starts

    heights = {
        "padd-top": config["TOP_PADDING"],
        "banner": globals.BANNER_HEIGHT,
        "maze": maze_height,
        "padd-bottom": config["BOT_PADDING"],
    }

    cols = globals.TERMINAL_SIZE.columns
    menu_h = compute_menu_layout(COMMANDS, cols).height
    rects: dict[str, Rect] = {
        "extra-left":  Rect(0, 0, xt_l, total_height),
        "padd-left":   Rect(xt_l, 0, padd_l, total_height),
        "padd-right":  Rect(x_right, 0, padd_r, total_height),
        "extra-right": Rect(x_right + padd_r, 0, xt_r, total_height),
        "menu":        Rect(0, total_height, cols, menu_h),
    }

    y = 0
    for name in globals.MID_REGION_ORDER:       # same order render() stacks them in
        rects[name] = Rect(x_mid, y, maze_width, heights[name])
        y += heights[name]

    return rects
