"""
convert_pixel_art.py

One-off conversion tool: PNG (native size, no scaling -- typically exported
from Pixilart, but could come from anywhere) -> a compact binary pixel-art
format.

Transparency: a source pixel is opaque iff alpha == 255. Anything else
(including partial alpha) is fully transparent -- no threshold, no blending,
matching how ANSI itself has no concept of partial alpha.

DEV-TIME tool only, requires Pillow (`pip install Pillow`). The binary
format needs no third-party library to read back -- just the stdlib
`struct` module (see art_loader.py).

Usage:
    python convert_pixel_art.py path/to/art.png path/to/output.pxart

Binary format (all multi-byte integers little-endian):
    magic           4 bytes   b"AMZP"
    version         1 byte
    width           2 bytes   uint16
    height          2 bytes   uint16
    palette_count   1 byte    n (0-255)
    palette         n * 3 bytes   RGB triples, in index order
    pixels          width*height bytes
                    one palette index per cell; the value == palette_count
                    means "transparent" (real colors are indices 0..n-1)
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

from PIL import Image

MAGIC = b"AMZP"
VERSION = 1
MAX_COLORS = 255  # index 255 (or fewer, == palette_count) is reserved for transparent


def convert(png_path: Path) -> tuple[int, int, list[tuple[int, int, int]], bytes]:
    """
    Read the PNG at native size (no resizing) and return
    (width, height, colors, indices):
      - colors: list of (r, g, b), ordered by palette index
      - indices: bytes of length width*height, one palette index per cell;
        a value == len(colors) means "transparent"
    """
    img = Image.open(png_path).convert("RGBA")
    width, height = img.size

    palette: dict[tuple[int, int, int], int] = {}
    raw_indices: list[int] = []  # -1 placeholder for transparent, fixed up below

    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            assert isinstance(pixel, tuple) and len(pixel) == 4, (
                f"expected an RGBA tuple at ({x}, {y}), got {pixel!r} "
                "-- convert('RGBA') above should guarantee this"
            )
            r, g, b, a = pixel

            if a != 255:
                raw_indices.append(-1)
                continue

            color = (r, g, b)
            idx = palette.get(color)
            if idx is None:
                if len(palette) >= MAX_COLORS:
                    raise ValueError(
                        f"Image has more than {MAX_COLORS} unique opaque colors "
                        "-- reduce the palette in your art tool."
                    )
                idx = len(palette)
                palette[color] = idx
            raw_indices.append(idx)

    # sentinel is guaranteed distinct from every real index (0..palette_count-1),
    # regardless of how many colors were used -- no separate reserved value needed
    sentinel = len(palette)
    indices = bytes(sentinel if v == -1 else v for v in raw_indices)

    colors = [color for color, _ in sorted(palette.items(), key=lambda kv: kv[1])]
    return width, height, colors, indices


def write_binary(
    out_path: Path,
    width: int,
    height: int,
    colors: list[tuple[int, int, int]],
    indices: bytes,
) -> None:
    with open(out_path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<B", VERSION))
        f.write(struct.pack("<HH", width, height))
        f.write(struct.pack("<B", len(colors)))
        for r, g, b in colors:
            f.write(struct.pack("<BBB", r, g, b))
        f.write(indices)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("png_path", type=Path, help="Path to the source PNG")
    parser.add_argument("out_path", type=Path, help="Path to write the .pxart binary file")
    args = parser.parse_args()

    width, height, colors, indices = convert(args.png_path)
    write_binary(args.out_path, width, height, colors, indices)

    n_transparent = indices.count(len(colors))
    size = args.out_path.stat().st_size
    print(
        f"Wrote {args.out_path} ({width}x{height} pixels, {len(colors)} colors, "
        f"{n_transparent} transparent cells, {size} bytes)"
    )


if __name__ == "__main__":
    main()
