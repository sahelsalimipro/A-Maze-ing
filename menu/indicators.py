from typing import Any
from abc import ABC, abstractmethod

import globals

class Indicator(ABC):

    width: int
    propertykey: str
    _config: dict[str, Any]

    def __init__(self, property: str) -> None:
        self.propertykey = property
        self._config = globals.CONFIG
        return
    
    @abstractmethod
    def __str__(self) -> str:
        ...

class BoolIndicator(Indicator):

    def __init__(self, property: str) -> None:
        super().__init__(property)
        self.width = 3
        return

    def __str__(self) -> str:
        return "ON " if self._config[self.propertykey] else "OFF"

class StrIndicator(Indicator):

    def __init__(self, property: str) -> None:
        super().__init__(property)
        self.width = 12
        return

    def __str__(self) -> str:
        return self._config[self.propertykey]
