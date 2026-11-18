from abc import ABC, abstractmethod

import globals


class Indicator(ABC):

    """A live value shown next to a command, read from the config."""
    width: int
    propertykey: str

    def __init__(self, property: str) -> None:
        """Show the value of the setting named property."""
        self.propertykey = property
        return

    @abstractmethod
    def __str__(self) -> str:
        """The text to display."""
        ...


class BoolIndicator(Indicator):

    """Shows a bool setting as ON or OFF."""
    def __init__(self, property: str) -> None:
        """Show the bool setting named property."""
        super().__init__(property)
        self.width = 3
        return

    def __str__(self) -> str:
        """"ON " or "OFF" (same width)."""
        return "ON " if globals.CONFIG.get(self.propertykey, False) else "OFF"


class StrIndicator(Indicator):

    """Shows a str setting as is."""
    def __init__(self, property: str) -> None:
        """Show the str setting named property."""
        super().__init__(property)
        self.width = 12
        return

    def __str__(self) -> str:
        """The current value of the setting."""
        return globals.CONFIG.get(self.propertykey, "")
