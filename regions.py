from typing import Any, TYPE_CHECKING

from drawers import Drawer
from pixels import Pixel

if TYPE_CHECKING:
    from dimensions import Rect


class Region():

    name: str
    width: int
    height: int
    buf: list[list[Pixel]]
    drawer: Drawer | None
    dirty: set[tuple[int, int]]

    def __init__(self, name: str, rect: Rect) -> None:
        self.name = name
        self.origin = (rect.x, rect.y)
        self.width, self.height = rect.w, rect.h
        self.buf = [
            [Pixel() for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.drawer = None
        self.dirty = set()

    def __eq__(self, value: object) -> bool:
        return value == self.name
    
    def attach(self, drawer: Drawer) -> None:
        self.drawer = drawer

    # Rendering called
    def fill_buffer(self, config: dict[str, Any]) -> None:
        if not self.drawer:
            raise NotImplementedError("Drawer undefined")

        self.drawer.draw(self.buf, config)

    def update(self, dt: float) -> None:
        if not self.drawer:
                raise NotImplementedError("Drawer undefined")
        self.drawer.update(self.buf, dt, self._mark)

    def _mark(self, x: int, y: int) -> None:
        self.dirty.add((x, y))
        return

    def consume_dirty(self) -> list[tuple[int, int]]:
        out = sorted(self.dirty, key=lambda p: (p[1], p[0]))
        self.dirty.clear()
        return out
