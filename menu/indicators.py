from typing import Any
from abc import ABC, abstractmethod

import globals


class Indicator(ABC):

    width: int
    propertykey: str

    def __init__(self, property: str) -> None:
        self.propertykey = property
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
        return "ON " if globals.CONFIG.get(self.propertykey, False) else "OFF"


class StrIndicator(Indicator):

    def __init__(self, property: str) -> None:
        super().__init__(property)
        self.width = 12
        return

    def __str__(self) -> str:
        return globals.CONFIG.get(self.propertykey, "")
