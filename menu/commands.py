from typing import Literal
from collections.abc import Callable

from .indicators import Indicator, BoolIndicator, StrIndicator
from .input_commands import (
    recolor, change_theme, new_seed, regenerate,
    toggle_solve, toggle_theme, exit_prog,
)

INPUT_COMMAND = Literal["c", "s", "r", "n", "t", "y", "e"]


class Command:
    """One action of the menu, triggered by a key."""
    def __init__(
        self,
        name: str,
        description: str,
        input: INPUT_COMMAND,
        func: Callable[[], bool],
        indicator: Indicator | None = None,
    ) -> None:
        """Create a command.

        Args:
            name: shown in the menu (upper-cased).
            description: shown under the name.
            input: the key that triggers it.
            func: the action; returns True to ask for a full redraw.
            indicator: optional live value shown in the menu.
        """
        self.name: str = name.upper()
        self.description: str = description
        self.input: INPUT_COMMAND = input
        self.func: Callable[[], bool] = func
        self.indicator = indicator
        return


COMMANDS: tuple[Command, ...] = (
    Command("Change colors", "Randomly changes the colors", "c", recolor),
    Command("Solve/Unsolve", "Toggles the state: solved & unsolved",
            "s", toggle_solve, BoolIndicator("SOLVED")),
    Command("Regenerate", "Remake the maze (with same seed)", "r", regenerate),
    Command("New seed", "Remake the maze (with a new seed)", "n", new_seed),
    Command("Theme on/off", "Enables or disable the use of theme",
            "t", toggle_theme, BoolIndicator("THEME_ON")),
    Command("Change theme", "Change theme", "y", change_theme,
            StrIndicator("THEME_NAME")),
    Command("Exit", "Exit the program", "e", exit_prog)
)

COMMAND_TABLE: dict[INPUT_COMMAND, Command] = {
    com.input: com for com in COMMANDS}
