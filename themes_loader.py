from __future__ import annotations
from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING
import logging
import inspect

from errors import ConfigErr
if TYPE_CHECKING:
    from amazeing import Maze
    from drawers import Drawer
    from config import Settings

logger = logging.getLogger(__name__)

def load_theme_module(name: str) -> ModuleType:
    """Loads theme module, raises ConfigErr if not found"""

    module_name = f"themes.{name}"
    try:
        module: ModuleType = import_module(module_name)
    except ModuleNotFoundError as e:
        if e.name == module_name:  # the theme itself doesn't exist
            raise ConfigErr(f"Unknown theme {name!r}") from e
        raise ConfigErr(
            f"Theme {name!r} failed to import: missing module {e.name!r}"
        ) from e

    return module


def load_theme(module: ModuleType, config: Settings, maze: Maze) -> dict[str, Drawer]:
    """Executes "register" function in the given theme module.
    Raises ConfigErr if signature incorrect or missing"""

    # name = "pac_man" if module is "themes.pac_man"
    name = module.__name__.rpartition(".")[2]
    register = getattr(module, "register", None)
    if not callable(register):
        raise ConfigErr(f"Theme {name!r} has no register() function")

    try:
        inspect.signature(register).bind(config, maze)
    except TypeError as e:
        raise ConfigErr(f"Theme {name!r}'s register() has the wrong signature: {e}") from e

    try:
        drawers = register(config, maze)
    except Exception as e:
        raise ConfigErr(f"Theme {name!r}'s register() raised: {e}") from e

    if not isinstance(drawers, dict):
        raise ConfigErr(f"Theme {name!r}'s register() must return a dict, got {type(drawers).__name__}")

    return drawers
