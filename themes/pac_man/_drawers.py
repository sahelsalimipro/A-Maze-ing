from typing import Callable

from .values import COLORS, OUTSIDE_GAP, INSIDE_GAP, WALL_SIZE  # , HEIGHT
from config import Settings
from drawers import Drawer  # , MazeDrawer, MenuDrawer
from pixels import Pixel


class PacManDrawer(Drawer):

    """Pac-Man style padding: walls and pac-gums (work in progress)."""
    def __init__(self) -> None:
        """Nothing to set up."""
        pass

    def draw(self, buffer: list[list[Pixel]], config: Settings) -> None:
        # height: int = HEIGHT
        # width: int = len(buffer[0])

        """Draw the gaps, walls and a row of pac-gums."""
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

    def update(
            self,
            buffer: list[list[Pixel]],
            dt: float,
            mark: Callable[[int, int], None]
    ) -> None:

        """Nothing to animate."""
        pass
        return

    def _empty_line(self, idx: int, buffer: list[list[Pixel]]) -> None:
        """Paint row idx with the background color."""
        for px in buffer[idx]:
            px.bg_clr = COLORS.bg_clr
        return

    def _wall(self, idx: int, buffer: list[list[Pixel]]) -> None:
        """Paint row idx as a wall."""
        for px in buffer[idx]:
            px.bg_clr = COLORS.bg_clr
            # TODO finish this func

    def _draw_balls(self, idx: int, buffer: list[list[Pixel]]) -> None:
        """Paint row idx with a pac-gum every 3 columns."""
        for i, px in enumerate(buffer[idx]):
            px.bg_clr = COLORS.bg_clr
            if i % 3 == 1:
                px.char = "⬤"
                px.fg_clr = COLORS.ball_clr
        return
