# config.py
from __future__ import annotations
import os
import re
import logging
from dataclasses import dataclass
from typing import Any, Callable
import dotenv

from errors import ConfigErr

logger = logging.getLogger(__name__)


# ---------- Per-type parsers ---------- #
def parse_bool(raw: str) -> bool:
    v = raw.strip().upper()
    if v == "TRUE":
        return True
    if v == "FALSE":
        return False
    raise ValueError(f"expected TRUE or FALSE, got {raw!r}")


def parse_int(raw: str) -> int:
    res = int(raw.strip())
    if res < 0:
        raise ValueError("Negative value")
    return res


def parse_str(raw: str) -> str:
    return raw.strip().strip('"')


def parse_char(raw: str) -> str:
    s = parse_str(raw)
    if len(s) != 1:
        raise ValueError(f"expected exactly 1 character, got {raw!r}")
    return s


def parse_coordinates(raw: str) -> tuple[int, int] | None:
    raw = raw.strip()
    if raw.upper() == "NONE":
        return None
    parts = raw.split(",")
    if len(parts) != 2:
        raise ValueError(f"expected 'x,y', got {raw!r}")

    try:
        x, y = (int(p.strip()) for p in parts)
    except ValueError:
        raise ValueError(
            f"coordinates must be integers, got {raw!r}") from None

    if x < 0 or y < 0:
        raise ValueError(f"coordinates must be >= 0, got {raw!r}")
    return (x, y)


def parse_tile_ratio(raw: str) -> tuple[int, int]:
    parts = raw.strip().split(",")
    if len(parts) != 2:
        raise ValueError(f"expected 'int,int', got {raw!r}")
    w, h = (int(p.strip()) for p in parts)
    if w <= 0 or h <= 0:
        raise ValueError("tile ratio values must both be positive")
    return (w, h)


COLOR_RE = re.compile(r"^\(?\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)?$")


def parse_color(raw: str) -> tuple[int, int, int] | None:
    s = parse_str(raw)
    if s.upper() == "NONE":
        return None
    m = COLOR_RE.match(s)
    if not m:
        raise ValueError(f"expected 'NONE' or '(r,g,b)', got {raw!r}")
    r, g, b = (int(x) for x in m.groups())
    for name, ch in (("r", r), ("g", g), ("b", b)):
        if not (0 <= ch <= 255):
            raise ValueError(f"color channel {name}={ch} out of range 0-255")
    return (r, g, b)

#  obsolete -> themes checked later in themes_loader.py
# def parse_theme_name(raw: str) -> str:
#     s = parse_str(raw).lower()
#     if s not in VALID_THEMES:
#         raise ValueError(f"unknown theme {raw!r}, expected one of {sorted(VALID_THEMES)}")
#     return s


# ---------- Schema ---------- #
@dataclass
class FieldSpec:
    key: str
    parser: Callable[[str], Any]
    default: Any
    # True: bad/missing value aborts startup. False: log a warning + fall back to default.
    critical: bool = False


FIELDS: list[FieldSpec] = [
    FieldSpec("MAZE_WIDTH", parse_int, 20),
    FieldSpec("MAZE_HEIGHT", parse_int, 15),
    FieldSpec("SOLVED", parse_bool, False),
    FieldSpec("SEED", parse_int, 42, critical=True),
    FieldSpec("PERFECT", parse_bool, True, critical=True),
    FieldSpec("ENTRY", parse_coordinates, None),
    FieldSpec("EXIT", parse_coordinates, None),

    FieldSpec("TILE_RATIO", parse_tile_ratio, (3, 1), critical=True),
    FieldSpec("CENTER_MAZE", parse_bool, True),
    FieldSpec("DISPLAY_BANNER", parse_bool, True),
    FieldSpec("TOP_PADDING", parse_int, 2),
    FieldSpec("BOT_PADDING", parse_int, 2),
    FieldSpec("LEFT_PADDING", parse_int, 4),
    FieldSpec("RIGHT_PADDING", parse_int, 4),
    FieldSpec("EXPAND_COLOR_TO_FULL_TERMINAL", parse_bool, True),
    FieldSpec("ENTRYPOINT_CHAR", parse_char, "◇"),
    FieldSpec("EXITPOINT_CHAR", parse_char, "◎"),

    FieldSpec("BACKGROUND_CLR", parse_color, None),
    FieldSpec("WALLS_CLR", parse_color, None),
    FieldSpec("TRAIL_CLR", parse_color, None),
    FieldSpec("ENTRYPOINT_CLR", parse_color, None),
    FieldSpec("EXITPOINT_CLR", parse_color, None),
    FieldSpec("TOP_PADDING_CLR", parse_color, None),
    FieldSpec("BOT_PADDING_CLR", parse_color, None),
    FieldSpec("LEFT_PADDING_CLR", parse_color, None),
    FieldSpec("RIGHT_PADDING_CLR", parse_color, None),
    FieldSpec("BANNER_TITLE_CLR", parse_color, None),
    FieldSpec("BANNER_FRAME_CLR", parse_color, None),
    FieldSpec("BANNER_BCKG_CLR", parse_color, None),

    FieldSpec("BANNER_TITLE", parse_str, "AMAZEING"),
    FieldSpec("BANNER_TOP_CHAR", parse_str, "─"),
    FieldSpec("BANNER_BOT_CHAR", parse_str, "─"),
    FieldSpec("BANNER_LEFT_CHAR", parse_str, "│"),
    FieldSpec("BANNER_RIGHT_CHAR", parse_str, "│"),
    FieldSpec("BANNER_CORNER_TOPLEFT_CHAR", parse_char, "┌"),
    FieldSpec("BANNER_CORNER_TOPRIGHT_CHAR", parse_char, "┐"),
    FieldSpec("BANNER_CORNER_BOTLEFT_CHAR", parse_char, "└"),
    FieldSpec("BANNER_CORNER_BOTRIGHT_CHAR", parse_char, "┘"),

    FieldSpec("THEME_ON", parse_bool, False),
    FieldSpec("THEME_NAME", parse_str, "default"),
]


def load_config() -> dict[str, Any]:
    if not dotenv.load_dotenv():
        raise ConfigErr()

    values: dict[str, Any] = {}
    critical_errors: list[str] = []

    for spec in FIELDS:
        raw = os.getenv(spec.key)

        if raw is None:
            if spec.critical:
                critical_errors.append(f"{spec.key} is missing (required)")
            else:
                logger.warning("%s not set, using default %r",
                               spec.key, spec.default)
            values[spec.key] = spec.default
            continue

        try:
            values[spec.key] = spec.parser(raw)
        except ValueError as e:
            if spec.critical:
                critical_errors.append(f"{spec.key}={raw!r} is invalid: {e}")
            else:
                logger.warning(
                    "%s=%r is invalid (%s), using default %r", spec.key, raw, e, spec.default)
                values[spec.key] = spec.default

    if critical_errors:
        raise ConfigErr("Invalid configuration:\n" +
                        "\n".join(f"  - {e}" for e in critical_errors))

    return values
