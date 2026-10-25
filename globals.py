from os import get_terminal_size, terminal_size
from typing import Literal, Any

from menu import Command, INPUT_COMMAND, recolor, toggle_solve, regenerate, new_seed, toggle_theme, change_theme, BoolIndicator, StrIndicator

# ----------     config    ---------- #
CONFIG: dict[str, Any]

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


# ----------      Menu     ---------- #
COMMANDS: tuple[Command, ...] = (
    Command("Change colors", "Randomly changes the colors", "c", recolor),
    Command("Solve/Unsolve", "Toggles the state: solved & unsolved", "s", toggle_solve, BoolIndicator("SOLVED")),
    Command("Regenerate", "Remake the maze (with same seed)", "r", regenerate),
    Command("New seed", "Remake the maze (with a new seed)", "n", new_seed),
    Command("Theme on/off", "Enables or disable the use of theme", "t", toggle_theme),
    Command("Change theme", "Change theme", "y", change_theme)
)

COMMAND_TABLE: dict[INPUT_COMMAND, Command] = { com.input: com for com in COMMANDS }

LABELS = ("Press:", "Name:", "Indicator:", "Description:")
LABEL_W = max(len(l) for l in LABELS)
MARGIN = 1
TEXT_X = MARGIN + LABEL_W + 1          # where every value starts
MIN_TEXT_W = 10                        # below this, wrapping is pointless
BLOCK_GAP = 1                          # blank lines between commands

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
