"""Single source of truth for themes.

A theme is a package in themes/ that load_theme_module() accepts: it
imports, and defines a callable register(config, maze). Everything else
(listing themes, picking the active one, building drawers) goes through
the functions below.
"""
from __future__ import annotations
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING
import logging
import inspect

import globals
from errors import ConfigErr
if TYPE_CHECKING:
    from maze import Maze
    from drawers import Drawer
    from config import Settings

logger = logging.getLogger(__name__)

THEMES_DIR = Path(__file__).parent / "themes"
DEFAULT_THEME = "default"

_available: tuple[str, ...] | None = None


def load_theme_module(name: str) -> ModuleType:
    """Imports a theme and checks it is usable. Raises ConfigErr if not."""

    module_name = f"themes.{name}"
    try:
        module: ModuleType = import_module(module_name)
    except ModuleNotFoundError as e:
        if e.name == module_name:  # the theme itself doesn't exist
            raise ConfigErr(f"Unknown theme {name!r}") from e
        raise ConfigErr(
            f"Theme {name!r} failed to import: missing module {e.name!r}"
        ) from e

    register = getattr(module, "register", None)
    if not callable(register):
        raise ConfigErr(f"Theme {name!r} has no register() function")
    try:
        inspect.signature(register).bind(None, None)    # (config, maze)
    except TypeError as e:
        raise ConfigErr(
            f"Theme {name!r}'s register() has the wrong signature: {e}"
        ) from e

    return module


def available_themes() -> tuple[str, ...]:
    """Names of every theme load_theme_module() accepts, sorted.
    Computed once; rejected themes are logged."""
    global _available
    if _available is None:
        names: list[str] = []
        for d in sorted(THEMES_DIR.iterdir()):
            if not (d / "__init__.py").is_file():
                continue
            try:
                load_theme_module(d.name)
            except ConfigErr as e:
                logger.warning("Theme %r skipped: %s", d.name, e)
                continue
            names.append(d.name)
        _available = tuple(names)
    return _available


def active_theme_name(config: Settings) -> str:
    """The theme the config asks for: THEME_NAME if THEME_ON, else default."""
    return config["THEME_NAME"] if config["THEME_ON"] else DEFAULT_THEME


def activate_theme(config: Settings) -> ModuleType:
    """Loads the active theme and applies its OVERRIDES to the config.
    Raises ConfigErr if the theme isn't usable."""
    module = load_theme_module(active_theme_name(config))
    config.apply_theme(getattr(module, "OVERRIDES", {}))
    return module


def load_theme(
    module: ModuleType, config: Settings, maze: Maze
) -> dict[str, Drawer]:
    """Runs the theme's register() and checks it returned a drawer for
    every region. Raises ConfigErr otherwise."""

    name = module.__name__.rpartition(".")[2]
    try:
        drawers = module.register(config, maze)
    except Exception as e:
        raise ConfigErr(f"Theme {name!r}'s register() raised: {e}") from e

    if not isinstance(drawers, dict):
        raise ConfigErr(
            f"Theme {name!r}'s register() must return a dict, "
            f"got {type(drawers).__name__}")

    missing = [r for r in globals.REGIONS_NAMES if r not in drawers]
    if missing:
        raise ConfigErr(
            f"Theme {name!r}'s register() has no drawer for: "
            f"{', '.join(missing)}")

    return drawers
