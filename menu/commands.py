from typing import Literal
from collections.abc import Callable

from .indicators import Indicator, BoolIndicator, StrIndicator
from .input_commands import recolor, change_theme, new_seed, regenerate, toggle_solve, toggle_theme, exit_prog

INPUT_COMMAND = Literal["c", "s", "r", "n", "t", "y", "e"]


class Command:
    def __init__(
        self,
        name: str,
        description: str,
        input: INPUT_COMMAND,
        func: Callable[..., None],
        indicator: Indicator | None = None,
    ) -> None:
        self.name: str = name.upper()
        self.description: str = description
        self.input: INPUT_COMMAND = input
        self.func: Callable[..., None] = func
        self.indicator = indicator
        return


COMMANDS: tuple[Command, ...] = (
    Command("Change colors", "Randomly changes the colors", "c", recolor),
    Command("Solve/Unsolve", "Toggles the state: solved & unsolved",
            "s", toggle_solve, BoolIndicator("SOLVED")),
    Command("Regenerate", "Remake the maze (with same seed)", "r", regenerate),
    Command("New seed", "Remake the maze (with a new seed)", "n", new_seed),
    Command("Theme on/off", "Enables or disable the use of theme",
            "t", toggle_theme),
    Command("Change theme", "Change theme", "y", change_theme),
    Command("Exit", "Exit the program", "e", exit_prog)
)

COMMAND_TABLE: dict[INPUT_COMMAND, Command] = {
    com.input: com for com in COMMANDS}
