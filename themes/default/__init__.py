from __future__ import annotations
from typing import TYPE_CHECKING, Any

from drawers import EmptyDrawer, MenuDrawer
from ._drawers import BaseDrawer, BannerDrawer, DefaultMazeDrawer
from amazeing import Maze
if TYPE_CHECKING:
    from drawers import Drawer
# from dev.helper_drawer import NumericalDrawer

def register(config: dict[str, Any], maze: Maze) -> dict[str, Drawer]:

    padd_top_bg_clr = config["TOP_PADDING_CLR"]
    padd_bot_bg_clr = config["BOT_PADDING_CLR"]
    padd_left_bg_clr = config["LEFT_PADDING_CLR"]
    padd_right_bg_clr = config["RIGHT_PADDING_CLR"]

    xtr, xtl= None, None

    if config["EXPAND_COLOR_TO_FULL_TERMINAL"]:
        xtl = BaseDrawer(padd_left_bg_clr)
        xtr = BaseDrawer(padd_right_bg_clr)
    else:
        xtl = EmptyDrawer()
        xtr = EmptyDrawer()

    return {
        "extra-left" : xtl,
        "padd-left" : BaseDrawer(padd_left_bg_clr),
        "padd-right" : BaseDrawer(padd_right_bg_clr),
        "extra-right" : xtr,
        "padd-top" : BaseDrawer(padd_top_bg_clr),
        "banner" : BannerDrawer(config),
        "maze" : DefaultMazeDrawer(maze, config),
        "padd-bottom" : BaseDrawer(padd_bot_bg_clr),
        "menu" : MenuDrawer()
    }
