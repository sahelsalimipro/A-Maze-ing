"""
art_loader.py

Reads a compact binary pixel-art file (produced by convert_pixel_art.py)
and draws it onto a buffer. No third-party dependency -- only stdlib
`struct`.

Two-step API, same shape as before:
- load_art(data): parse the binary format into an ArtData object. Call
  once, e.g. at Drawer construction.
- build_palette(art): one Pixel per unique color. Also call once.
- stamp(buffer, art, palette, x=0, y=0): write the art onto an existing
  buffer at (x, y). A cell whose index == len(palette) is transparent
  and is left untouched -- whatever the buffer already held there shows
  through.

This module never allocates or sizes a buffer itself -- buffer size and
ownership stay with whatever set the buffer up in the first place.

Loading a bundled asset from within an installed package should go
through importlib.resources rather than a hardcoded relative path, so it
keeps working regardless of how the package ends up installed (wheel,
zipapp, editable install, etc.):

    from importlib.resources import files
    data = files(__package__).joinpath("border.pxart").read_bytes()
    art = load_art(data)

Usage in a Drawer, e.g.:

    from importlib.resources import files
    from .art_loader import load_art, build_palette, stamp

    class BorderDrawer(Drawer):
        def __init__(self):
            data = files(__package__).joinpath("border.pxart").read_bytes()
            self._art = load_art(data)
            self._palette = build_palette(self._art)

        def draw(self, buffer):
            stamp(buffer, self._art, self._palette, x=0, y=0)

        def update(self, buffer, dt):
            pass  # static art, nothing to animate
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

from pixels import Pixel

MAGIC = b"AMZP"
VERSION = 1

_HEADER_FORMAT = "<4sBHHB"  # magic, version, width, height, palette_count
_HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)


@dataclass
class ArtData:
    width: int
    height: int
    colors: list[tuple[int, int, int]]
    indices: bytes  # width*height palette indices; len(colors) == transparent


def load_art(data: bytes) -> ArtData:
    """Parse a .pxart binary blob into an ArtData object."""
    magic, version, width, height, palette_count = struct.unpack_from(
        _HEADER_FORMAT, data, 0
    )
    if magic != MAGIC:
        raise ValueError(f"not a pxart file (bad magic: {magic!r})")
    if version != VERSION:
        raise ValueError(f"unsupported pxart version: {version}")

    offset = _HEADER_SIZE
    colors: list[tuple[int, int, int]] = []
    for _ in range(palette_count):
        r, g, b = struct.unpack_from("<BBB", data, offset)
        colors.append((r, g, b))
        offset += 3

    pixel_count = width * height
    indices = data[offset : offset + pixel_count]
    if len(indices) != pixel_count:
        raise ValueError(
            f"truncated pxart file: expected {pixel_count} pixel bytes, "
            f"got {len(indices)}"
        )

    return ArtData(width=width, height=height, colors=colors, indices=indices)


def build_palette(art: ArtData) -> list[Pixel]:
    """One Pixel per unique color, indexed the same as art.colors."""
    return [Pixel(" ", color, color) for color in art.colors]


def stamp(
    buffer: list[list[Pixel]],
    art: ArtData,
    palette: list[Pixel],
    x: int = 0,
    y: int = 0,
) -> None:
    """
    Write art onto buffer in place, top-left corner at (x, y).
    A pixel index == len(palette) is transparent: that cell is left as-is.
    """
    transparent = len(palette)
    i = 0
    for row_offset in range(art.height):
        target_row = buffer[y + row_offset]
        for col_offset in range(art.width):
            idx = art.indices[i]
            i += 1
            if idx != transparent:
                target_row[x + col_offset] = palette[idx]
