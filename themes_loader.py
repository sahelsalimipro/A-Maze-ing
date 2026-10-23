from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING, Any
import logging
import inspect

from errors import ConfigErr
if TYPE_CHECKING:
    from amazeing import Maze
    from drawers import Drawer

logger = logging.getLogger(__name__)

def load_theme(name: str, config: dict[str, Any], maze: Maze) -> dict[str, Drawer]:
    module_name = f"themes.{name}"
    try:
        module: ModuleType = import_module(module_name)
    except ModuleNotFoundError as e:
        raise ConfigErr(f"Unknown theme {name!r}") from e

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
