from __future__ import annotations
from typing import TYPE_CHECKING
from os import terminal_size
from shutil import get_terminal_size

if TYPE_CHECKING:
    from types import ModuleType
    from config import Settings
    from regions import Region
    from maze import Maze

# ----------     config    ---------- #
CONFIG: Settings

# ----------   App state   ---------- #
THEME_MODULE: ModuleType            # theme currently loaded
REGIONS: dict[str, Region] = {}
MAZE: Maze

# ----------   Rendering   ---------- #
FPS: int = 12
MAX_DT: float = 0.25
T_FRAME: float = 1 / FPS
STEP: float = 1 / 60  # 60 hertz for the simulation (pulling inputs)
VIEW_Y: int = 0
VIEW_X: int = 0

# ----------    Terminal   ---------- #
TERMINAL_SIZE: terminal_size = get_terminal_size()

# ----------   Junctions   ---------- #
JUNCTIONS_CHARS = {
    frozenset({"N"}): "│", frozenset({"S"}): "│",
    frozenset({"E"}): "─", frozenset({"W"}): "─",

    frozenset({"N", "S"}): "│", frozenset({"E", "W"}): "─",
    frozenset({"N", "E"}): "└", frozenset({"N", "W"}): "┘",
    frozenset({"S", "E"}): "┌", frozenset({"S", "W"}): "┐",

    frozenset({"N", "S", "E"}): "├", frozenset({"N", "S", "W"}): "┤",
    frozenset({"N", "E", "W"}): "┴", frozenset({"S", "E", "W"}): "┬",

    frozenset({"N", "S", "E", "W"}): "┼",
}

# ----------     Regions    ---------- #
REGIONS_NAMES: tuple = (
    "extra-left", "padd-left",
    "padd-right", "extra-right",
    "padd-top", "banner", "maze", "padd-bottom",
    "menu"
)


# ---------- Middle regions ---------- #
MID_REGION_ORDER: tuple = ("padd-top", "banner", "maze", "padd-bottom")

MID_WIDTH: int | None = None

# ----------     Banner     ---------- #
BANNER_HEIGHT: int = 5
