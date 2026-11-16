from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tiles import BaseTile

class InvalidTileErr(ValueError):

    def __init__(
        self,
        tile: BaseTile,
        msg: str = "Invalid tile",
        *args: object
    ) -> None:
        self.tile = tile
        self.msg = msg
        self.full_msg = f"{msg}\nInfo: {self.tile}"
        super().__init__(self.full_msg, *args)


class MazeErr(Exception):

    def __init__(self, msg: str="Unkown error"):
        super().__init__(f"Maze Error: {msg}")
