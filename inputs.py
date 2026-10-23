from typing import TypeGuard, get_args
from collections.abc import Callable
import sys

from globals import COMMAND_TABLE, INPUT_COMMAND

def recolor() -> None:
    pass

def toggle_solve() -> None:
    pass

def regenerate() -> None:
    pass

def new_seed() -> None:
    pass

def toggle_theme() -> None:
    pass

def change_theme() -> None:
    pass



def is_command(value: str) -> TypeGuard[INPUT_COMMAND]:
    return value in COMMAND_TABLE

def handle_inputs() -> bool:
    line = sys.stdin.readline()
    if not line:
        return False

    key = line.strip()
    if not is_command(key):
        return False

    COMMAND_TABLE[key].func()
    return True
