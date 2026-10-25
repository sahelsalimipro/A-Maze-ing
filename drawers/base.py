from abc import ABC, abstractmethod
from typing import Any, Callable

from pixels import Pixel
from .utils import _center
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
        return

    def draw(self, buffer: list[list[Pixel]], config: dict[str, Any]) -> None:
        # TODO ensure menu dimensions to be big enough

        height = len(buffer)
        width = len(buffer[0])


        title = " Actions "
        len_t = len(title)
        padd = width - len_t
        padd_left = padd // 2

        for i in range(padd_left):
            buffer[0][i].char = '-'
        for i in range(len_t):
            buffer[0][i + padd_left].char = title[i]
        for i in range(padd - padd_left):
            buffer[0][i + padd_left + len_t].char = '-'

        columns = {
            "Press:" : [],
            "Command:": [],
            "Indicator:" : [],
            "Description:" : []
        }

        for c in COMMANDS:
            columns["Press:"].append(c.input)
            columns["Command:"].append(c.name)
            columns["Indicator:"].append(c.indicator)
            columns["Descripton:"].append(c.description)

        lens = []
        for name, values in columns.items():
            if name in ("Description:", "Indicator:"): #nah, not really what I want...
                lens.append(len(name))
                continue

            lens.append(max(values, key=len))

        return

    def update(
            self,
            buffer: list[list[Pixel]],
            dt: float,
            mark: Callable[[int, int], None]
        ) -> None:
        return
