from __future__ import annotations
from typing import TYPE_CHECKING

from drawers import EmptyDrawer, MenuDrawer
from ._drawers import BaseDrawer, BannerDrawer, DefaultMazeDrawer
from maze import Maze
from menu import COMMANDS
from config import Settings
if TYPE_CHECKING:
    from drawers import Drawer
# from dev.helper_drawer import NumericalDrawer


def register(config: Settings, maze: Maze) -> dict[str, Drawer]:

    """Return the drawer of every region for the default theme."""
    xtl: Drawer
    xtr: Drawer
    if config["EXPAND_COLOR_TO_FULL_TERMINAL"]:
        xtl = BaseDrawer("LEFT_PADDING_CLR")
        xtr = BaseDrawer("RIGHT_PADDING_CLR")
    else:
        xtl = EmptyDrawer()
        xtr = EmptyDrawer()

    return {
        "extra-left": xtl,
        "padd-left": BaseDrawer("LEFT_PADDING_CLR"),
        "padd-right": BaseDrawer("RIGHT_PADDING_CLR"),
        "extra-right": xtr,
        "padd-top": BaseDrawer("TOP_PADDING_CLR"),
        "banner": BannerDrawer(config),
        "maze": DefaultMazeDrawer(maze, config),
        "padd-bottom": BaseDrawer("BOT_PADDING_CLR"),
        "menu": MenuDrawer(COMMANDS)
    }
