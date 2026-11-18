from typing import Callable

from .values import COLORS, HEIGHT, OUTSIDE_GAP, INSIDE_GAP, WALL_SIZE
from config import Settings
from drawers import Drawer, MazeDrawer, MenuDrawer
from pixels import Pixel

class PacManDrawer(Drawer):

    def __init__(self) -> None:
        pass

    def draw(self, buffer: list[list[Pixel]], config: Settings) -> None:
        height: int = HEIGHT
        width: int = len(buffer[0])

        idx: int = 0
        #  Outside Gap
        for i in range(OUTSIDE_GAP):
            self._empty_line(idx, buffer)
            idx += 1

        #  Wall top
        self._wall(idx, buffer)
        idx += WALL_SIZE

        #  Inside Gap
        for i in range(INSIDE_GAP):
            self._empty_line(idx, buffer)
            idx += 1

        #  Ball
        self._draw_balls(idx, buffer)
        idx += 1

        #  Inside Gap
        for i in range(INSIDE_GAP):
            self._empty_line(idx, buffer)
            idx += 1

        #  Wall bottom
        self._wall(idx, buffer)
        idx += WALL_SIZE

        #  Outside Gap
        for i in range(OUTSIDE_GAP):
            self._empty_line(idx, buffer)
            idx += 1

        return

    def update(self, buffer: list[list[Pixel]], dt: float, mark: Callable[[int, int], None]) -> None:
        pass
        return

    def _empty_line(self, idx: int, buffer: list[list[Pixel]]) -> None:
        for px in buffer[idx]:
            px.bg_clr = COLORS.bg_clr
        return

    def _wall(self, idx: int, buffer: list[list[Pixel]]) -> None:
        pass

    def _draw_balls(self, idx: int, buffer: list[list[Pixel]]) -> None:
        for i, px in enumerate(buffer[idx]):
            if i % 3 == 0:
                pass
        pass
