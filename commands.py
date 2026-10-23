from typing import TYPE_CHECKING, Any
from collections.abc import Callable

if TYPE_CHECKING:
    from globals import INPUT_COMMAND

class Command:
    def __init__(
        self,
        name: str,
        description: str,
        input: INPUT_COMMAND,
        func: Callable[..., None],
        indicator: Any = None,
    ) -> None:
        self.name: str = name.upper()
        self.description: str = description
        self.input: INPUT_COMMAND = input
        self.func: Callable[..., None] = func
        self.indicator: Any = indicator
        pass # TODO
