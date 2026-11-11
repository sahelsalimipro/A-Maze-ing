from __future__ import annotations
from typing import TYPE_CHECKING, Any

from drawers import MazeDrawer, MenuDrawer
from menu import COMMANDS
from themes.default._drawers import BannerDrawer
from ._drawers import (
    FAR, NEAR, QuoteDirector, RainDrawer, SequenceDrawer
)
from .quotes import QUOTES
from amazeing import Maze
from config import Settings
if TYPE_CHECKING:
    from drawers import Drawer


BG = (3, 10, 5)                 # almost black, a hint of green
GREEN = (0, 255, 65)            # "matrix green"
DARK_GREEN = (0, 143, 17)

OVERRIDES: dict[str, Any] = {
    # Layout: centred, so both sides get the same amount of rain
    "CENTER_MAZE": True,
    "DISPLAY_BANNER": True,
    "TOP_PADDING": 3,
    "BOT_PADDING": 3,
    "LEFT_PADDING": 4,
    "RIGHT_PADDING": 4,
    "EXPAND_COLOR_TO_FULL_TERMINAL": True,

    "ENTRYPOINT_CHAR": "◇",
    "EXITPOINT_CHAR": "◎",

    # Colors
    "BACKGROUND_CLR": BG,
    "WALLS_CLR": DARK_GREEN,
    "TRAIL_CLR": GREEN,
    "TOP_PADDING_CLR": BG,
    "BOT_PADDING_CLR": BG,
    "LEFT_PADDING_CLR": BG,
    "RIGHT_PADDING_CLR": BG,

    # Banner
    "BANNER_TITLE": "A M A Z E T R I X",
    "BANNER_TITLE_CLR": GREEN,
    "BANNER_FRAME_CLR": DARK_GREEN,
    "BANNER_BCKG_CLR": BG,
    "BANNER_TOP_CHAR": "═",
    "BANNER_BOT_CHAR": "═",
    "BANNER_LEFT_CHAR": "║",
    "BANNER_RIGHT_CHAR": "║",
    "BANNER_CORNER_TOPLEFT_CHAR": "╔",
    "BANNER_CORNER_TOPRIGHT_CHAR": "╗",
    "BANNER_CORNER_BOTLEFT_CHAR": "╚",
    "BANNER_CORNER_BOTRIGHT_CHAR": "╝",
}

# Repeating sequences of the strips above and below the banner/maze
TOP_SEQUENCE = "╳ ░▒▓▒░ ╳ ▚▞▚▞ "
BOT_SEQUENCE = "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁ "


def register(config: Settings, maze: Maze) -> dict[str, Drawer]:
    quotes = QuoteDirector(QUOTES)      # shared: no repeats across regions

    left_bg = config["LEFT_PADDING_CLR"]
    right_bg = config["RIGHT_PADDING_CLR"]

    return {
        "extra-left": RainDrawer(FAR, left_bg, quotes),
        "padd-left": RainDrawer(NEAR, left_bg, quotes),
        "padd-right": RainDrawer(NEAR, right_bg, quotes),
        "extra-right": RainDrawer(FAR, right_bg, quotes),
        "padd-top": SequenceDrawer(
            TOP_SEQUENCE, (0, 120, 30), config["TOP_PADDING_CLR"], scroll=2.0
        ),
        "banner": BannerDrawer(config),
        "maze": MazeDrawer(maze, config),
        "padd-bottom": SequenceDrawer(
            BOT_SEQUENCE, (0, 90, 25), config["BOT_PADDING_CLR"]
        ),
        "menu": MenuDrawer(COMMANDS),
    }
