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


def parse_coord(raw: str) -> tuple[int, int] | None:
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


def parse_ratio(raw: str) -> tuple[int, int]:
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

# ---------- Per-type checkers ---------- #
def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)   # True is an int!

def check_int(v: Any) -> int:
    if not _is_int(v):
        raise ValueError(f"expected int, got {v!r}")
    if v < 0:
        raise ValueError(f"expected >= 0, got {v}")
    return int(v)

def check_bool(v: Any) -> bool:
    if not isinstance(v, bool):
        raise ValueError(f"expected bool, got {v!r}")
    return v

def check_color(v: Any) -> tuple[int, int, int] | None:
    if v is None:
        return None
    if not (isinstance(v, (tuple, list)) and len(v) == 3
            and all(_is_int(c) and 0 <= c <= 255 for c in v)):
        raise ValueError(f"expected None or (r,g,b) in 0-255, got {v!r}")
    return (v[0], v[1], v[2])

def check_str(v: Any) -> str:
    if not isinstance(v, str) or not v:
        raise ValueError(f"expected str with min_len = 1, got {v!r}")
    return v

def check_char(v: Any) -> str:
    if not isinstance(v, str) or len(v) != 1:
        raise ValueError(f"expected exactly 1 character, got {v!r}")
    return v

def check_coord(v: Any) -> tuple[int, int] | None:
    if v is None:
        return None
    if not (isinstance(v, (tuple, list)) and len(v) == 2
            and all(_is_int(c) and c >= 0 for c in v)):
        raise ValueError(f"expected None or (x, y) with x, y >= 0, got {v!r}")
    return (v[0], v[1])

def check_ratio(v: Any) -> tuple[int, int]:
    if not (isinstance(v, (tuple, list)) and len(v) == 2
            and all(_is_int(c) and c > 0 for c in v)):
        raise ValueError(f"expected two positive ints, got {v!r}")
    return tuple(v)


# ---------- Schema ---------- #
@dataclass
class FieldType:
    convert: Callable[[str], Any]
    check: Callable[[Any], Any]


BOOL  = FieldType(parse_bool,  check_bool)
INT   = FieldType(parse_int,   check_int)
STR   = FieldType(parse_str,   check_str)
CHAR  = FieldType(parse_char,  check_char)
COORD = FieldType(parse_coord, check_coord)
COLOR = FieldType(parse_color, check_color)
RATIO = FieldType(parse_ratio, check_ratio)

@dataclass
class FieldSpec:
    key: str
    type: FieldType
    default: Any
    themeable: bool = True
    # True: bad/missing value aborts startup. False: log a warning + fall back to default.
    critical: bool = False

    def parse(self, raw: str) -> Any:        # .env only
        return self.type.check(self.type.convert(raw))

    def check(self, value: Any) -> Any:      # theme + runtime
        return self.type.check(value)


FIELDS: list[FieldSpec] = [
    FieldSpec("MAZE_WIDTH", INT, 20, themeable=False),
    FieldSpec("MAZE_HEIGHT", INT, 15, themeable=False),
    FieldSpec("SOLVED", BOOL, False, themeable=False),
    FieldSpec("SEED", INT, 42, themeable=False, critical=True),
    FieldSpec("PERFECT", BOOL, True, themeable=False, critical=True),
    FieldSpec("ENTRY", COORD, None, themeable=False),
    FieldSpec("EXIT", COORD, None, themeable=False),

    FieldSpec("TILE_RATIO", RATIO, (3, 1), critical=True),
    FieldSpec("CENTER_MAZE", BOOL, True),
    FieldSpec("DISPLAY_BANNER", BOOL, True),
    FieldSpec("TOP_PADDING", INT, 2),
    FieldSpec("BOT_PADDING", INT, 2),
    FieldSpec("LEFT_PADDING", INT, 4),
    FieldSpec("RIGHT_PADDING", INT, 4),
    FieldSpec("EXPAND_COLOR_TO_FULL_TERMINAL", BOOL, True),
    FieldSpec("ENTRYPOINT_CHAR", CHAR, "◇"),
    FieldSpec("EXITPOINT_CHAR", CHAR, "◎"),

    FieldSpec("BACKGROUND_CLR", COLOR, None),
    FieldSpec("WALLS_CLR", COLOR, None),
    FieldSpec("TRAIL_CLR", COLOR, None),
    FieldSpec("ENTRYPOINT_CLR", COLOR, None),
    FieldSpec("EXITPOINT_CLR", COLOR, None),
    FieldSpec("TOP_PADDING_CLR", COLOR, None),
    FieldSpec("BOT_PADDING_CLR", COLOR, None),
    FieldSpec("LEFT_PADDING_CLR", COLOR, None),
    FieldSpec("RIGHT_PADDING_CLR", COLOR, None),
    FieldSpec("BANNER_TITLE_CLR", COLOR, None),
    FieldSpec("BANNER_FRAME_CLR", COLOR, None),
    FieldSpec("BANNER_BCKG_CLR", COLOR, None),

    FieldSpec("BANNER_TITLE", STR, "AMAZEING"),
    FieldSpec("BANNER_TOP_CHAR", STR, "─"),
    FieldSpec("BANNER_BOT_CHAR", STR, "─"),
    FieldSpec("BANNER_LEFT_CHAR", STR, "│"),
    FieldSpec("BANNER_RIGHT_CHAR", STR, "│"),
    FieldSpec("BANNER_CORNER_TOPLEFT_CHAR", CHAR, "┌"),
    FieldSpec("BANNER_CORNER_TOPRIGHT_CHAR", CHAR, "┐"),
    FieldSpec("BANNER_CORNER_BOTLEFT_CHAR", CHAR, "└"),
    FieldSpec("BANNER_CORNER_BOTRIGHT_CHAR", CHAR, "┘"),

    FieldSpec("THEME_ON", BOOL, False, themeable=False),
    FieldSpec("THEME_NAME", STR, "default", themeable=False),
    FieldSpec("OUTPUT_FILE", STR, "maze.txt")
]

SPECS: dict[str, FieldSpec] = {f.key: f for f in FIELDS}

class Settings(Mapping[str, Any]):
    """Read-only for consumers. Lookup order: runtime > theme > base."""

    def __init__(self, base: dict[str, Any], specs: Mapping[str, FieldSpec]) -> None:
        self._specs = specs
        self._theme: dict[str, Any] = {}
        self._runtime: dict[str, Any] = {}
        self._chain = ChainMap(self._runtime, self._theme, dict(base))

    def __getitem__(self, key: str) -> Any:
        return self._chain[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._chain)

    def __len__(self) -> int:
        return len(self._chain)

    def _spec(self, key: str) -> FieldSpec:
        try:
            return self._specs[key]
        except KeyError:
            raise ValueError(f"unknown setting {key!r}") from None

    def apply_theme(self, overrides: Mapping[str, Any]) -> None:
        self._theme.clear()
        for key, value in overrides.items():
            try:
                spec = self._spec(key)
                if not spec.themeable:
                    raise ValueError("not overridable by a theme")
                self._theme[key] = spec.check(value)
            except ValueError as e:
                logger.warning("Theme override %s=%r rejected (%s), "
                               "keeping the base value", key, value, e)
        for key in [k for k in self._runtime if self._specs[k].themeable]:
            del self._runtime[key]           # recolors from the old theme

    def set(self, key: str, value: Any) -> None:
        self._runtime[key] = self._spec(key).check(value)


def load_config() -> Settings:
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
            values[spec.key] = spec.parse(raw)          # convert + check
        except ValueError as e:
            if spec.critical:
                critical_errors.append(f"{spec.key}={raw!r} is invalid: {e}")
            else:
                logger.warning("%s=%r is invalid (%s), using default %r",
                               spec.key, raw, e, spec.default)
                values[spec.key] = spec.default

    if critical_errors:
        raise ConfigErr("Invalid configuration:\n" +
                        "\n".join(f"  - {e}" for e in critical_errors))

    return Settings(values, SPECS)
