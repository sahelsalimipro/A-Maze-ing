from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Literal, Generator, TYPE_CHECKING

from errors import InvalidTileErr
from dirs import DIRS, OPP_DIR, Direction
if TYPE_CHECKING:
    from amazeing import Maze

# ---------- Generating IDs ---------- #
def id_gen() -> Generator[str]:
    id = 0
    while True:
        id += 1
        yield str(id)

ID_GEN = id_gen()


# -------------------- Tiles -------------------- #
class BaseTile(ABC):

    id: str
    isLogo: bool
    isLimit: bool
    isSolution: bool
    neighbours: dict[Direction, BaseTile | None]
    walls: dict[Direction, bool]
    wallscount: int
    coords: tuple[int, int]
    x: int
    y: int

    def __lt__(self, other: BaseTile) -> bool:
        return (self.y, self.x) < (other.y, other.x)

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __init__(self, coords: tuple[int, int], maze: Maze) -> None:
        self.maze_ref = maze
        self.id = next(ID_GEN)
        self.isSolution = False
        self.coords = coords
        self.x = coords[0]
        self.y = coords[1]
        self.neighbours = { dir: None for dir in DIRS }
        self.wallscount = 0
        self._set_walls()

    @abstractmethod
    def _set_walls(self) -> None: ...

    @abstractmethod
    def goto(self, direction: Direction) -> BaseTile | Literal[False]: ...


class Tile(BaseTile):
    def __init__(self, coords: tuple[int, int], maze: Maze) -> None:

        self.isLogo = False
        self.isLimit = False
        super().__init__(coords, maze)

    def __str__(self) -> str:
        return f"[Tile {self.id} - x:{self.x} y:{self.y}]"

    def _set_walls(self) -> None:
        self.walls = { dir : True for dir in DIRS }
        self.wallscount = sum(self.walls.values())

    def goto(self, direction: Direction) -> BaseTile | Literal[False]:
        if self.walls[direction]:
            return False
        next_tile = self.neighbours[direction]
        if not next_tile:
            raise InvalidTileErr(self, "Invalid reference to neighbour")
        return next_tile


class Limit(BaseTile):
    def __init__(self, coords: tuple[int, int], maze: Maze) -> None:

        self.isLimit = True
        self.isLogo = False
        super().__init__(coords, maze)

    def __str__(self) -> str:
        return f"[Limit {self.id} - x:{self.x} y:{self.y}]"

    def _set_walls(self) -> None:
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
        raise InvalidTileErr(self, "Navigation from limit forbidden")

class LogoTile(BaseTile):
    def __str__(self) -> str:
        return f"[Logo {self.id} - x:{self.x} y:{self.y}]"

    def __init__(self, coords: tuple[int, int], maze: Maze) -> None:
        self.isLogo = True
        self.isLimit = False
        super().__init__(coords, maze)

    def _set_walls(self) -> None:
        self.walls = { d : True for d in DIRS }
        self.wallscount = 4

    def goto(self, direction: Direction) -> BaseTile | Literal[False]:
        raise InvalidTileErr(self, "Navigation from logo tile forbidden")
