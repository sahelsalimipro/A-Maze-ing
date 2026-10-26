from os import get_terminal_size, terminal_size
from typing import Literal, Any

# from menu import Command, INPUT_COMMAND, COMMANDS, COMMAND_TABLE

# ----------     config    ---------- #
CONFIG: dict[str, Any]

# ----------   Rendering   ---------- #
FPS: int = 12
MAX_DT: float = 0.25
T_FRAME: float = 1 / FPS
STEP: float = 1 / 60  # 60 hertz for the simulation (pulling inputs)

# ----------    Terminal   ---------- #
TERMINAL_SIZE: terminal_size = get_terminal_size()

# ----------     Themes    ---------- #
# VALID_THEMES: set[str] = {"matrix", "nyan-cat", "pac-man", "peach-castle"}
# probably obsolete, since themes_loader.py checks dynamically ?

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
