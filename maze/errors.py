from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tiles import BaseTile


class InvalidTileErr(ValueError):

    """An operation that is not allowed on this tile."""
    def __init__(
        self,
        tile: BaseTile,
        msg: str = "Invalid tile",
        *args: object
    ) -> None:
        """Create the error; the message includes the tile's description."""
        self.tile = tile
        self.msg = msg
        self.full_msg = f"{msg}\nInfo: {self.tile}"
        super().__init__(self.full_msg, *args)


class MazeErr(Exception):

    """Invalid maze parameters, or a maze that cannot be solved."""
    def __init__(self, msg: str = "Unkown error"):
        """Create the error with a "Maze Error: " prefix."""
        super().__init__(f"Maze Error: {msg}")
