from typing import Any

from drawers import Drawer
from pixels import Pixel


class NumericalDrawer(Drawer):
    """Visually helping drawer, to see dimensions.
    Prints out numbers for rows and cols"""

    fg_clr = (30, 0, 60)
    bg_clr = (204, 255, 0)

    def draw(self, buffer: list[list[Pixel]], config: dict[str, Any]) -> None:
        for y, row in enumerate(buffer):
            for x, px in enumerate(row):
                if y == 0 or y == len(buffer) - 1:
                    px.char = str(x + 1)[-1]
                elif x == 0 or x == len(row) - 1 :
                    px.char = str(y + 1)[-1]
                px.fg_clr = self.fg_clr
                px.bg_clr = self.bg_clr
        return

    def update(self, buffer: list[list[Pixel]], dt: float) -> None:
        return
