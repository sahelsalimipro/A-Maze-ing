from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Literal, Generator, TYPE_CHECKING

from .errors import InvalidTileErr
from .dirs import DIRS, Direction
if TYPE_CHECKING:
    from .amazeing import Maze

# ---------- Generating IDs ---------- #


def id_gen() -> Generator[str]:
    """Yield unique tile ids: "1", "2", ..."""
    id = 0
    while True:
        id += 1
        yield str(id)


ID_GEN = id_gen()


# -------------------- Tiles -------------------- #
class BaseTile(ABC):

    """One position of the grid, with its walls and neighbours.

    Attributes:
        x, y: grid coordinates (the border ring is at 0).
        walls: True for each closed side ("N", "S", "W", "E").
        wallscount: number of closed sides.
        neighbours: the adjacent tile on each side, or None.
        isLogo: True for the cells of the 42.
        isLimit: True for the border ring.
        isSolution: True for the cells of the path, after
            Maze.resolve().
    """
    id: str
    isLogo: bool
    isLimit: bool
    isSolution: bool
    visited: bool
    neighbours: dict[Direction, BaseTile | None]
    walls: dict[Direction, bool]
    wallscount: int
    coords: tuple[int, int]
    x: int
    y: int

    def __lt__(self, other: BaseTile) -> bool:
        """Order tiles by row, then column (for heaps and sorting)."""
        return (self.y, self.x) < (other.y, other.x)

    @abstractmethod
    def __str__(self) -> str:
        """Short description of the tile, for error messages."""

    @abstractmethod
    def __init__(self, coords: tuple[int, int], maze: Maze) -> None:
        """Create the tile at grid position coords, in maze."""
        self.maze_ref = maze
        self.id = next(ID_GEN)
        self.isSolution = False
        self.visited = False
        self.coords = coords
        self.x = coords[0]
        self.y = coords[1]
        self.neighbours = {dir: None for dir in DIRS}
        self.wallscount = 0
        self._set_walls()

    @abstractmethod
    def _set_walls(self) -> None:
        """Set the initial walls of the tile."""

    @abstractmethod
    def goto(self, direction: Direction) -> BaseTile | Literal[False]:
        """Return the neighbour on that side, or False if a wall is closed."""


class Tile(BaseTile):
    """A normal cell. Starts with its four walls closed."""
    def __init__(self, coords: tuple[int, int], maze: Maze) -> None:

        """Create the cell at grid position coords, in maze."""
        self.isLogo = False
        self.isLimit = False
        super().__init__(coords, maze)

    def __str__(self) -> str:
        """Short description of the tile, for error messages."""
        return f"[Tile {self.id} - x:{self.x} y:{self.y}]"

    def _set_walls(self) -> None:
        """Close all four walls."""
        self.walls = {dir: True for dir in DIRS}
        self.wallscount = sum(self.walls.values())

    def goto(self, direction: Direction) -> BaseTile | Literal[False]:
        """Return the neighbour on that side, or False if a wall is closed.

        Raises:
            InvalidTileErr: if the neighbour is missing.
        """
        if self.walls[direction]:
            return False
        next_tile = self.neighbours[direction]
        if not next_tile:
            raise InvalidTileErr(self, "Invalid reference to neighbour")
        return next_tile


class Limit(BaseTile):
    """A tile of the border ring around the maze. Never carved."""
    def __init__(self, coords: tuple[int, int], maze: Maze) -> None:

        """Create the border tile at grid position coords, in maze."""
        self.isLimit = True
        self.isLogo = False
        super().__init__(coords, maze)

    def __str__(self) -> str:
        """Short description of the tile, for error messages."""
        return f"[Limit {self.id} - x:{self.x} y:{self.y}]"

    def _set_walls(self) -> None:
        """Close only the side facing the maze (none for the corners)."""
        max_x = self.maze_ref.width + 1
        max_y = self.maze_ref.height + 1
        self.walls = {dir: False for dir in DIRS}

        is_corner = self.x in (0, max_x) and self.y in (0, max_y)
        if not is_corner:
            if self.x == 0:
                self.walls["E"] = True
            elif self.x == max_x:
                self.walls["W"] = True
            elif self.y == 0:
                self.walls["S"] = True
            elif self.y == max_y:
                self.walls["N"] = True

        self.wallscount = sum(self.walls.values())

    def goto(self, direction: Direction) -> BaseTile | Literal[False]:
        """Moving from the border is not allowed.

        Raises:
            InvalidTileErr: always.
        """
        raise InvalidTileErr(self, "Navigation from limit forbidden")


class LogoTile(BaseTile):
    """A cell of the 42. Fully closed and never carved."""
    def __str__(self) -> str:
        """Short description of the tile, for error messages."""
        return f"[Logo {self.id} - x:{self.x} y:{self.y}]"

    def __init__(self, coords: tuple[int, int], maze: Maze) -> None:
        """Create the 42 cell at grid position coords, in maze."""
        self.isLogo = True
        self.isLimit = False
        super().__init__(coords, maze)

    def _set_walls(self) -> None:
        """Close all four walls."""
        self.walls = {d: True for d in DIRS}
        self.wallscount = 4

    def goto(self, direction: Direction) -> BaseTile | Literal[False]:
        """Moving from a 42 cell is not allowed.

        Raises:
            InvalidTileErr: always.
        """
        raise InvalidTileErr(self, "Navigation from logo tile forbidden")
