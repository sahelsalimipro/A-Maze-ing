from abc import ABC, abstractmethod
from typing import Any, Callable

from pixels import Pixel
from globals import COMMANDS

class Drawer(ABC):

    @abstractmethod
    def draw(self, buffer: list[list[Pixel]], config: dict[str, Any]) -> None:
        ...

    @abstractmethod
    def update(
        self,
        buffer: list[list[Pixel]],
        dt: float,
        mark: Callable[[int, int], None]
    ) -> None:
        """Updates pixels and marks them for the renderer"""
        ...

class EmptyDrawer(Drawer):
    """Draws empty space in default terminal color"""

    def draw(self, buffer: list[list[Pixel]], config: dict[str, Any]) -> None:
        return

    def update(
            self,
            buffer: list[list[Pixel]],
            dt: float,
            mark: Callable[[int, int], None]
        ) -> None:
        return

class MenuDrawer(Drawer):
    """Draws a menu"""

    def __init__(self) -> None:
