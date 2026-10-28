from typing import TYPE_CHECKING, Any, Callable

from .utils import _scale, _center
from .base import Drawer
from globals import JUNCTIONS_CHARS
from amazeing import Maze

if TYPE_CHECKING:
    from pixels import Pixel, PixelKind
    # from tiles import BaseTile


# Index = bitmask of filled quadrants: UL=1, UR=2, LL=4, LR=8
QUADRANT_GLYPHS = " ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█"


def _blocks(v: int, ratio: int) -> tuple[int, int]:
    """Cell index of the first and second half of buffer coordinate `v`.

    On a wall line, the two halves belong to two different cells;
    inside a cell, both halves belong to the same one.
    """
    step = ratio + 1
    if v % step == 0:                  # on a wall line
        return v // step - 1, v // step
    return v // step, v // step


_GLYPHS: dict[tuple[str, str], str] = {
    ("mid", "mid"):      "○",
    ("mid", "left"):     "▐",
    ("mid", "right"):    "▌",
    ("top", "mid"):      "▄",
    ("bottom", "mid"):   "▀",
    ("top", "left"):     "▗",
    ("top", "right"):    "▖",
    ("bottom", "left"):  "▝",
    ("bottom", "right"): "▘",
}


def _content_placements(
    ratio_x: int, ratio_y: int
) -> dict[tuple[int, int], str]:

    if ratio_y % 2:
        rows = [((ratio_y - 1) // 2, "mid")]
    else:
        rows = [(ratio_y // 2 - 1, "top"), (ratio_y // 2, "bottom")]

    if ratio_x % 2:
        cols = [((ratio_x - 1) // 2, "mid")]
    else:
        cols = [(ratio_x // 2 - 1, "left"), (ratio_x // 2, "right")]

    return {
        (dy, dx): _GLYPHS[(rtag, ctag)]
        for dy, rtag in rows
        for dx, ctag in cols
    }


# def _is_logo(tile: BaseTile | None) -> bool:
#     return tile is not None and tile.isLogo


class MazeDrawer(Drawer):
    def __init__(self, maze: Maze, config: dict[str, Any]) -> None:
        self.maze = maze
        self.ratio: tuple[int, int] = config["TILE_RATIO"]
        self.bg_clr: tuple[int, int, int] = config["BACKGROUND_CLR"]
        self.wall_clr: tuple[int, int, int] = config["WALLS_CLR"]
        self.trail_clr: tuple[int, int, int] = config["TRAIL_CLR"]
        self.entry_clr: tuple[int, int, int] = config["ENTRYPOINT_CLR"]
        self.exit_clr: tuple[int, int, int] = config["EXITPOINT_CLR"]

        self._kind_colors: dict[PixelKind, tuple[int, int, int] | None] = {
            "content": self.trail_clr,
            "wall": self.wall_clr,
            "junction": self.wall_clr,
            "empty": self.bg_clr
        }

        self._start_char = config["ENTRYPOINT_CHAR"]
        self._goal_char = config["EXITPOINT_CHAR"]
        return

    def draw(self, buffer: list[list[Pixel]], config: dict[str, Any]) -> None:
        self.fill_buffer(buffer)
        self._colorize(buffer)
        self._paint_logo(buffer)
        return

    def update(
        self,
        buffer: list[list[Pixel]],
        dt: float,
        mark: Callable[[int, int], None]
    ) -> None:
        return

    def fill_buffer(self, buffer: list[list[Pixel]]) -> None:
        ratio_x, ratio_y = self.ratio
        inner = [row[1:-1] for row in self.maze.grid[1:-1]]
        ct_rows, ct_cols = len(inner), len(inner[0])
        placements = _content_placements(ratio_x, ratio_y)

        self._logo_px: set[tuple[int, int]] = set()

        for r_idx, row in enumerate(inner):
            cy = _scale(r_idx, ratio_y)
            for c_idx, tile in enumerate(row):
                cx = _scale(c_idx, ratio_x)

                if tile.isLogo:
                    # the cell + its ring of walls and corners
                    self._logo_px.update(
                        (y, x)
                        for y in range(cy - 1, cy + ratio_y + 1)
                        for x in range(cx - 1, cx + ratio_x + 1)
                    )

                for dy in range(ratio_y):
                    for dx in range(ratio_x):
                        px = buffer[cy + dy][cx + dx]
                        px.kind = "content"
                        if tile.isSolution and (dy, dx) in placements:
                            px.char = placements[dy, dx]
                            px.fg_clr = self.trail_clr

                if tile.walls["N"]:
                    for dx in range(ratio_x):
                        px = buffer[cy - 1][cx + dx]
                        px.char = "─"
                        px.kind = "wall"
                if tile.walls["S"]:
                    for dx in range(ratio_x):
                        px = buffer[cy + ratio_y][cx + dx]
                        px.char = "─"
                        px.kind = "wall"
                if tile.walls["W"]:
                    for dy in range(ratio_y):
                        px = buffer[cy + dy][cx - 1]
                        px.char = "│"
                        px.kind = "wall"
                if tile.walls["E"]:
                    for dy in range(ratio_y):
                        px = buffer[cy + dy][cx + ratio_x]
                        px.char = "│"
                        px.kind = "wall"

        self._fill_junctions(buffer, ct_rows, ct_cols)
        self._draw_markers(buffer)
        return

    def _fill_junctions(self, buffer: list[list[Pixel]], ct_rows: int, ct_cols: int) -> None:
        ratio_x, ratio_y = self.ratio
        buf_h, buf_w = len(buffer), len(buffer[0])

        def is_wall(y: int, x: int) -> bool:
            return 0 <= y < buf_h and 0 <= x < buf_w and buffer[y][x].kind == "wall"

        for r in range(ct_rows + 1):
            y = r * (ratio_y + 1)
            for c in range(ct_cols + 1):
                x = c * (ratio_x + 1)
                dirs = frozenset({
                    d for d, ok in (
                        ("N", is_wall(y - 1, x)), ("S", is_wall(y + 1, x)),
                        ("W", is_wall(y, x - 1)), ("E", is_wall(y, x + 1)),
                    ) if ok
                })
                if dirs:
                    px = buffer[y][x]
                    px.char = JUNCTIONS_CHARS[dirs]
                    px.kind = "junction"
        return

    def _draw_markers(self, buffer: list[list[Pixel]]) -> None:
        ratio_x, ratio_y = self.ratio
        mid_x = (ratio_x - 1) // 2
        mid_y = (ratio_y - 1) // 2

        for tile, char in (
            (self.maze._start, self._start_char),
            (self.maze._goal,  self._goal_char),
        ):
            # Grid coords include the Limit ring, the buffer doesn't: subtract 1
            cx = _scale(tile.x - 1, ratio_x)
            cy = _scale(tile.y - 1, ratio_y)
            px = buffer[cy + mid_y][cx + mid_x]
            px.char = char
        return

    def _colorize(self, buffer: list[list[Pixel]]) -> None:
        for y, row in enumerate(buffer):
            for x, px in enumerate(row):
                if (y, x) in self._logo_px:
                    px.fg_clr = px.bg_clr = self.wall_clr  # char invisible
                else:
                    px.fg_clr = self._kind_colors.get(px.kind)
                    px.bg_clr = self.bg_clr
        return

    def _paint_logo(self, buffer: list[list[Pixel]]) -> None:
        ratio_x, ratio_y = self.ratio
        inner = [row[1:-1] for row in self.maze.grid[1:-1]]

        def is_logo(r: int, c: int) -> bool:
            return (0 <= r < len(inner) and 0 <= c < len(inner[0])
                    and inner[r][c].isLogo)

        for y, x in self._logo_px:
            top, bottom = _blocks(y, ratio_y)
            left, right = _blocks(x, ratio_x)
            mask = (is_logo(top, left) * 1 | is_logo(top, right) * 2
                    | is_logo(bottom, left) * 4 | is_logo(bottom, right) * 8)
            px = buffer[y][x]
            px.char = QUADRANT_GLYPHS[mask]
            px.fg_clr = self.wall_clr
            px.bg_clr = self.bg_clr
