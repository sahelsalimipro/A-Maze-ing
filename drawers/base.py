from abc import ABC, abstractmethod
from typing import Any, Callable

from pixels import Pixel
from .utils import _center
from globals import COMMANDS, MARGIN, LABELS
from menu import compute_menu_layout, Command, MenuLayout

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

    commands: tuple[Command, ...]

    def __init__(self, commands: tuple[Command, ...]) -> None:
        self.commands = commands
        self.layout: MenuLayout | None = None
        return

    @staticmethod
    def _put(buffer: list[list[Pixel]], y: int, x: int, text: str) -> None:
        for i, ch in enumerate(text):
            buffer[y][x + i].char = ch

    def draw(self, buffer: list[list[Pixel]], config: dict[str, Any]) -> None:
        width = len(buffer[0])
        lay = self.layout = compute_menu_layout(self.commands, width)
        self._put(buffer, 0, 0, " Actions ".center(width, "-"))

        for cmd, b in zip(self.commands, lay.blocks):
            self._put(buffer, b.y_press, MARGIN, LABELS[0])
            self._put(buffer, b.y_press, lay.text_x, cmd.input)

            self._put(buffer, b.y_name, MARGIN, LABELS[1])
            for i, line in enumerate(b.name_lines):
                self._put(buffer, b.y_name + i, lay.text_x, line)

            self._put(buffer, b.y_indicator, MARGIN, LABELS[2])
            self._put(buffer, b.y_indicator, lay.text_x, str(cmd.indicator))

            self._put(buffer, b.y_desc, MARGIN, LABELS[3])
            for i, line in enumerate(b.desc_lines):
                self._put(buffer, b.y_desc + i, lay.text_x, line)
            return

    def update(
            self,
            buffer: list[list[Pixel]],
            dt: float,
            mark: Callable[[int, int], None]
        ) -> None:
        return
