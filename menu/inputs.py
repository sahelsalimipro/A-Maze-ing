from enum import IntEnum
from typing import TypeGuard

import viewport
from .commands import COMMAND_TABLE, INPUT_COMMAND
from .keyboard import read_key


class Redraw(IntEnum):
    """What the screen needs after an input."""
    NONE = 0
    REPAINT = 1     # same buffers, shown somewhere else (scroll)
    REBUILD = 2     # drawers must draw again (commands)


# key -> (direction, by a whole page?). UP/DOWN/PGUP/PGDN come from read_key().
# The mouse wheel arrives as UP/DOWN in the alternate screen.
SCROLL_KEYS: dict[str, tuple[int, bool]] = {
    "UP": (-1, False), "k": (-1, False),
    "DOWN": (1, False), "j": (1, False),
    "PGUP": (-1, True),
    "PGDN": (1, True),
}


def is_command(value: str) -> TypeGuard[INPUT_COMMAND]:
    """True if value is the key of a command."""
    return value in COMMAND_TABLE


def handle_inputs() -> Redraw:
    """Handles the key pressed since the last call, if any.
    Never waits: the game loop keeps going when nobody types."""
    key = read_key()
    if key is None:
        return Redraw.NONE

    if key in SCROLL_KEYS:
        direction, by_page = SCROLL_KEYS[key]
        rows = direction * (viewport.page() if by_page else 1)
        return Redraw.REPAINT if viewport.scroll_by(rows) else Redraw.NONE

    if is_command(key) and COMMAND_TABLE[key].func():
        return Redraw.REBUILD
    return Redraw.NONE
