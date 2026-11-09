from __future__ import annotations
import os
import re
import logging
from dataclasses import dataclass
from typing import Any, Callable
import dotenv
from collections import ChainMap
from collections.abc import Iterator, Mapping

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


# ---------- Schema ---------- #
@dataclass
class FieldSpec:
    key: str
    parser: Callable[[str], Any]
    default: Any
    themeable: bool = True
    # True: bad/missing value aborts startup. False: log a warning + fall back to default.
    critical: bool = False


FIELDS: list[FieldSpec] = [
    FieldSpec("MAZE_WIDTH", parse_int, 20, themeable=False),
    FieldSpec("MAZE_HEIGHT", parse_int, 15, themeable=False),
    FieldSpec("SOLVED", parse_bool, False, themeable=False),
    FieldSpec("SEED", parse_int, 42, themeable=False, critical=True),
    FieldSpec("PERFECT", parse_bool, True, themeable=False, critical=True),
    FieldSpec("ENTRY", parse_coordinates, None, themeable=False),
    FieldSpec("EXIT", parse_coordinates, None, themeable=False),

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

    FieldSpec("THEME_ON", parse_bool, False, themeable=False),
    FieldSpec("THEME_NAME", parse_str, "default", themeable=False),
]

class Settings(Mapping[str, Any]):
    """Read-only for consumers. Lookup order: runtime > theme > base."""

    def __init__(self, base: Mapping[str, Any], themeable: frozenset[str]) -> None:
        self._themeable = themeable
        self._theme: dict[str, Any] = {}
        self._runtime: dict[str, Any] = {}
        self._chain: ChainMap[str, Any] = ChainMap(
            self._runtime, self._theme, dict(base))   # private copy of base

    def __getitem__(self, key: str) -> Any:
        return self._chain[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._chain)

    def __len__(self) -> int:
        return len(self._chain)

    def set(self, key: str, value: Any) -> None:       # the only runtime write path
        if key not in self._chain:
            raise KeyError(key)
        self._runtime[key] = value

    def apply_theme(self, overrides: Mapping[str, Any]) -> None:
        if bad := overrides.keys() - self._themeable:
            raise ConfigErr(f"Theme overrides non-themeable keys: {sorted(bad)}")
        self._theme.clear()
        self._theme.update(overrides)
        for key in self._runtime.keys() & self._themeable:   # drop stale recolors
            del self._runtime[key]

def load_config() -> Settings:
    if not dotenv.load_dotenv():
        raise ConfigErr()

    THEMEABLE: set[str] = set()

    values: dict[str, Any] = {}
    critical_errors: list[str] = []

    for spec in FIELDS:
        raw = os.getenv(spec.key)

        if spec.themeable == True:
            THEMEABLE.add(spec.key)

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

    return Settings(values, frozenset(THEMEABLE))
