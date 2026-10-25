from typing import Literal
from collections.abc import Callable

from .indicators import Indicator

INPUT_COMMAND = Literal["c", "s", "r", "n", "t", "y"]

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
