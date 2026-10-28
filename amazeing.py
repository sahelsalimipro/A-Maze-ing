import logging
from collections import namedtuple
from random import Random

from tiles import BaseTile, Tile, Limit, LogoTile
from dirs import DELTAS
from carve import pick_endpoints, wilson
from solvers import astar
import globals

logger = logging.getLogger(__name__)


LOGO_42: tuple[str, ...] = (
    "#...###",
    "#.#...#",
    "###.###",
    "..#.#..",
    "..#.###",
)


def logo_cells(
    width: int,
    height: int
) -> set[tuple[int, int]]:
    """Grid coordinates of the logo cells, centred in the maze."""

    pattern_h, pattern_w = 5, 7

    # +1 because grid coordinates include the Limit ring
    off_x = 1 + (width - pattern_w) // 2
    off_y = 1 + (height - pattern_h) // 2
    return {
        (off_x + dx, off_y + dy)
        for dy, row in enumerate(LOGO_42)
        for dx, ch in enumerate(row)
        if ch == "#"
    }


GenInfos = namedtuple('GenInfos', ['seed', 'loop_chance'])


class Maze():
    def __init__(self, dimensions: tuple[int, int], infos: GenInfos) -> None:
        self.dimensions = dimensions
        self.width = dimensions[0]
        self.height = dimensions[1]

        self.logo = logo_cells(self.width, self.height)

        self.seed = infos.seed
        self.loop_chance = infos.loop_chance
        self.grid = self._build_grid()
        self._rng = Random(self.seed)

        start, goal = globals.CONFIG.get("ENTRY"), globals.CONFIG.get("EXIT")
        self._start, self._goal = pick_endpoints(self, start, goal)
        self._carve(self.loop_chance)

        return

    def _build_grid(self) -> list[list[BaseTile]]:

        max_x = self.width + 1
        max_y = self.height + 1

        def _wire_neighbours(rows: list[list[BaseTile]]) -> None:
            # for each row
            for r in rows:
                # for each column/tile
                for tile in r:
                    # link in every direction
                    for dir, (dx, dy) in DELTAS.items():
                        nx, ny = tile.x + dx, tile.y + dy

                        if 0 <= nx <= max_x and 0 <= ny <= max_y:
                            tile.neighbours[dir] = rows[ny][nx]

        def is_edge(x, y) -> bool:
            return x == 0 or x == max_x or y == 0 or y == max_y

        def make_tile(x: int, y: int) -> BaseTile:
            if is_edge(x, y):
                return Limit((x, y), self)
            if (x, y) in self.logo:
                return LogoTile((x, y), self)
            return Tile((x, y), self)

        rows = [
            [make_tile(x, y) for x in range(max_x + 1)]
            for y in range(max_y + 1)
        ]
        _wire_neighbours(rows)
        return rows

    def _carve(self, loop_chance: float) -> None:
        return wilson(self, self._start, loop_chance)

    def resolve(self) -> None:
        path: list[BaseTile] | None = astar(self._start, self._goal)
        if path is None:
            logger.error("Created maze without a solution")
            raise ValueError("No path between starting point and end point")
        for t in path:
            t.isSolution = True
        return
