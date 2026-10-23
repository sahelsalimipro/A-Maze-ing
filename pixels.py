from dataclasses import dataclass
from typing import Literal

PixelKind = Literal["content", "wall", "junction", "empty"]

class Pixel:
    def __init__(self) -> None:
        self.char: str = " "
        self.fg_clr: tuple[int, int, int] | None = None
        self.bg_clr: tuple[int, int, int] | None = None
        self.kind: PixelKind = "empty"

def px_to_str(pixel: Pixel) -> str:
    """Render a single Pixel as an ANSI-colored string, resetting after."""
    codes = []
    if pixel.fg_clr is not None:
        r, g, b = pixel.fg_clr
        codes.append(f"\033[38;2;{r};{g};{b}m")
    if pixel.bg_clr is not None:
        r, g, b = pixel.bg_clr
        codes.append(f"\033[48;2;{r};{g};{b}m")

    if not codes:
        return pixel.char  # nothing to reset if no color was set

    return "".join(codes) + pixel.char + "\033[0m"
