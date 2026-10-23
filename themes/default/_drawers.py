from typing import Any, cast, Callable

from drawers import Drawer, MazeDrawer
from pixels import Pixel
from globals import BANNER_HEIGHT, MID_WIDTH
from drawers import _center, _fill_sequence


class BaseDrawer(Drawer):

    def __init__(self, bg_clr: tuple[int, int, int] | None) -> None:
        self._bg_clr = bg_clr
        return

    def draw(self, buffer: list[list[Pixel]], config: dict[str, Any]) -> None:
        for row in buffer:
            for px in row:
                px.bg_clr = self._bg_clr
        return

    def update(
                self,
                buffer: list[list[Pixel]],
                dt: float,
                mark: Callable[[int, int], None]
            ) -> None:
        return

class BannerDrawer(Drawer):

    def __init__(self, config: dict[str, Any]) -> None:
        self._title = config["BANNER_TITLE"]
        self._clr_fg = config["BANNER_TITLE_CLR"]
        self._clr_bckg = config["BANNER_BCKG_CLR"]
        self._borders = {
            "top"    : config["BANNER_TOP_CHAR"],
            "bottom" : config["BANNER_BOT_CHAR"],
            "left"   : config["BANNER_LEFT_CHAR"],
            "right"  : config["BANNER_RIGHT_CHAR"]
        }
        self._corners = {
            "top-left"      : config["BANNER_CORNER_TOPLEFT_CHAR"],
            "top-right"     : config["BANNER_CORNER_TOPRIGHT_CHAR"],
            "bottom-left"   : config["BANNER_CORNER_BOTLEFT_CHAR"],
            "bottom-right"  : config["BANNER_CORNER_BOTRIGHT_CHAR"],
        }
        return

    def draw(self, buffer: list[list[Pixel]], config: dict[str, Any]) -> None:
        height = len(buffer)
        if height == 0:
            return
        width = len(buffer[0])
        if height < 3 or width < 2:
            # Should never trigger, width is based on maze width and should
            # be intercepted before reaching here. Height is based on a
            # constant, defined by the dev for aesthetic purposes. Just don't
            # put less than 3 you dumbass >:(
            raise ValueError("Buffer allowed to Banner too small.")

        #  Manually set first and last rows, they have corners
        self._set_row(buffer[0],
                      self._corners["top-left"] +
                      _fill_sequence(self._borders["top"], width - 2) +
                      self._corners["top-right"]
                    )
    
        self._set_row(buffer[-1],
                      self._corners["bottom-left"] +
                      _fill_sequence(self._borders["bottom"], width - 2) +
                      self._corners["bottom-right"]
                    )

        inner_rows = buffer[1:-1]
        left_col = _fill_sequence(self._borders["left"], len(inner_rows))
        right_col = _fill_sequence(self._borders["right"], len(inner_rows))

        for i, row in enumerate(inner_rows):
            self._set_pixel(row[0], left_col[i])
            self._set_pixel(row[-1], right_col[i])
            for px in row[1:-1]:
                self._set_pixel(px, " ")

        if inner_rows:
            title_row = inner_rows[len(inner_rows) // 2]
            title = _center(self._title, width - 2)
            for px, ch in zip(title_row[1:-1], title):
                self._set_pixel(px, ch)

    def _set_row(self, row: list[Pixel], chars: str) -> None:
        for px, ch in zip(row, chars):
            self._set_pixel(px, ch)
        return

    def _set_pixel(self, px: Pixel, ch: str) -> None:
        px.char = ch
        px.fg_clr = self._clr_fg
        px.bg_clr = self._clr_bckg
        
        return

    def update(
                self,
                buffer: list[list[Pixel]],
                dt: float,
                mark: Callable[[int, int], None]
            ) -> None:
        return

class DefaultMazeDrawer(MazeDrawer):
    def draw(self, buffer: list[list[Pixel]], config: dict[str, Any]) -> None:
        return super().draw(buffer, config)

    def update(
                self,
                buffer: list[list[Pixel]],
                dt: float,
                mark: Callable[[int, int], None]
            ) -> None:
        return super().update(buffer, dt, mark)
