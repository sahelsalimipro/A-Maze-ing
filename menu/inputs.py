from typing import TypeGuard

from .commands import COMMAND_TABLE, INPUT_COMMAND
from .keyboard import read_key


def is_command(value: str) -> TypeGuard[INPUT_COMMAND]:
    return value in COMMAND_TABLE


def handle_inputs() -> bool:
    """Runs the command of the key pressed since the last call, if any.
    Never waits: the game loop keeps going when nobody types."""
    key = read_key()
    if key is None or not is_command(key):
        return False

    COMMAND_TABLE[key].func()
    return True
