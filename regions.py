from __future__ import annotations
from typing import TYPE_CHECKING

from drawers import Drawer
from pixels import Pixel

if TYPE_CHECKING:
    from dimensions import Rect
    from config import Settings


class Region():

    """A rectangle of the screen, with its pixels and its drawer.

    Pixels changed since the last frame are kept in dirty.
    """
    name: str
    width: int
    height: int
    buf: list[list[Pixel]]
    drawer: Drawer | None
    dirty: set[tuple[int, int]]

    def __init__(self, name: str, rect: Rect) -> None:
        """Create the region name at the position and size of rect."""
        self.name = name
        self.origin = (rect.x, rect.y)
        self.width, self.height = rect.w, rect.h
        self.buf = [[]]
        self.drawer = None
        self.dirty = set()

    def __eq__(self, value: object) -> bool:
        """A region is equal to its name."""
        return value == self.name

    def attach(self, drawer: Drawer) -> None:
        """Use drawer to fill this region."""
        self.drawer = drawer

    # Rendering called
    def fill_buffer(self, config: Settings) -> None:
        """Repaint the whole buffer with the drawer.

        Raises:
            NotImplementedError: if no drawer is attached.
        """
        if not self.drawer:
            raise NotImplementedError("Drawer undefined")

        self.drawer.draw(self.buf, config)

    def update(self, dt: float) -> None:
        """Let the drawer animate the buffer for dt seconds.

        Raises:
            NotImplementedError: if no drawer is attached.
        """
        if not self.drawer:
            raise NotImplementedError("Drawer undefined")
        self.drawer.update(self.buf, dt, self._mark)

    def _mark(self, x: int, y: int) -> None:
        """Mark pixel (x, y) as changed."""
        self.dirty.add((x, y))
        return

    def consume_dirty(self) -> list[tuple[int, int]]:
        """Return the changed pixels, sorted by row then column, and
        clear the list.
        """
        out = sorted(self.dirty, key=lambda p: (p[1], p[0]))
        self.dirty.clear()
        return out

    def redraw(self, config: Settings) -> None:
        """Rebuild the buffer from scratch and mark every pixel for output."""
        self.buf = [[Pixel() for _ in range(self.width)]
                    for _ in range(self.height)]
        self.dirty.clear()
        self.fill_buffer(config)
        self.mark_all()

    def mark_all(self) -> None:
        """Marks every pixel for output, e.g. after the view scrolled."""
        self.dirty = {(x, y) for y in range(self.height)
                      for x in range(self.width)}
