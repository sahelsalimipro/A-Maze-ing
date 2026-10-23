from os import get_terminal_size, terminal_size
from typing import Literal

from commands import Command
from input_commands import recolor, toggle_solve, regenerate, new_seed, toggle_theme, change_theme

# ----------   Rendering   ---------- #
FPS: int = 12
MAX_DT: float = 0.25
T_FRAME: float = 1 / FPS
STEP: float = 1 / 60 # 60 hertz for the simulation (pulling inputs)

# ----------    Terminal   ---------- #
TERMINAL_SIZE: terminal_size = get_terminal_size()

# ----------     Themes    ---------- #
# VALID_THEMES: set[str] = {"matrix", "nyan-cat", "pac-man", "peach-castle"}
# probably obsolete, since themes_loader.py checks dynamically ?


# ----------     Inputs    ---------- #
INPUT_COMMAND = Literal["c", "s", "r", "n", "t", "y"]

COMMANDS: tuple[Command, ...] = (
    Command("Change colors", "Randomly changes the colors of the maze", "c", recolor),
    Command("Solve/Unsolve", "Toggles the state of the maze between solved and unsolved", "s", toggle_solve, True),
    Command("Regenerate", "Remake the maze (with same seed)", "r", regenerate),
    Command("New seed", "Remake the maze (with a new seed)", "n", new_seed),
    Command("Theme on/off", "Enables or disable the use of theme", "t", toggle_theme),
    Command("Change theme", "Change theme", "y", change_theme)
)

COMMAND_TABLE: dict[INPUT_COMMAND, Command] = { com.input: com for com in COMMANDS }

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
