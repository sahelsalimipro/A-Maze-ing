from __future__ import annotations
import logging
from collections.abc import Callable
from random import Random

from .tiles import BaseTile, Tile, Limit, LogoTile
from .dirs import DELTAS
from .carve import pick_endpoints, wilson, find_components, dfs
from .solvers import astar, bfs
from .errors import MazeErr

logger = logging.getLogger(__name__)

LOGO_42: tuple[str, ...] = (
    "#...###",
    "#.....#",
    "###.###",
    "..#.#..",
    "..#.###",
)


# Smallest maze that fits the logo with one free cell all around it
LOGO_MIN_WIDTH = 9
LOGO_MIN_HEIGHT = 7


def logo_cells(
    width: int,
    height: int
) -> set[tuple[int, int]]:
    """Grid coordinates of the logo cells, centred in the maze.

    The pattern's centre cell (open) is placed on the maze's centre cell
    (width // 2, height // 2), so the centre is always a corridor, even
    when a dimension is even.

    Returns:
        The set of (x, y) grid coordinates of the logo cells, or an empty
        set if the maze is smaller than LOGO_MIN_WIDTH x LOGO_MIN_HEIGHT.
    """
    if width < LOGO_MIN_WIDTH or height < LOGO_MIN_HEIGHT:
        logger.warning(
            "Maze %dx%d is too small for the 42 pattern (min %dx%d): "
            "generated without it", width, height,
            LOGO_MIN_WIDTH, LOGO_MIN_HEIGHT)
        return set()

    pattern_h, pattern_w = len(LOGO_42), len(LOGO_42[0])

    # +1 because grid coordinates include the Limit ring
    off_x = 1 + width // 2 - pattern_w // 2
    off_y = 1 + height // 2 - pattern_h // 2
    return {
        (off_x + dx, off_y + dy)
        for dy, row in enumerate(LOGO_42)
        for dx, ch in enumerate(row)
        if ch == "#"
    }


class Maze():
    """A maze, generated and ready to solve.

    The grid has a ring of Limit tiles around the cells, so the
    maze's cell (x, y) is grid[y + 1][x + 1].

    Example:
        m = Maze(20, 15, seed=42)
        path = m.resolve()
        print(m)
    """
    def __init__(
        self, width, height,
        seed=None, perfect=True,
        entry=None, exit=None,
        carver="dfs", solver="bfs"
    ) -> None:

        """Generate a maze.

        Args:
            width: number of cells horizontally.
            height: number of cells vertically.
            seed: seed of the random generator; same seed and same
                parameters give the same maze. None for a random one.
            perfect: True for exactly one path between two cells, False
                for a board with loops and no dead ends.
            entry: (x, y) of the entry, 0-based, or None to pick one.
            exit: (x, y) of the exit, 0-based, or None to pick one.
            carver: generation algorithm, "dfs" or "wilson".
            solver: shortest-path algorithm, "bfs" or "astar".

        Raises:
            MazeErr: if the entry or exit is invalid (outside the maze,
                on the 42, equal, or not connected).
        """
        self.dimensions = width, height
        self.width = width
        self.height = height

        self.logo = logo_cells(self.width, self.height)

        self.seed = seed
        self.is_perfect = perfect
        self.grid = self._build_grid()
        self.components, self.component_of = find_components(self.grid)
        self._rng = Random(self.seed)

        start, goal = entry, exit
        self._start, self._goal = pick_endpoints(self, start, goal)

        if carver == "wilson":
            self._carve(wilson)
        else:
            self._carve(dfs)

        self._solver = solver

        return

    def _build_grid(self) -> list[list[BaseTile]]:

        """Create every tile (border, 42 or normal) and link neighbours.

        Returns:
            The rows of tiles, including the border ring.
        """
        max_x = self.width + 1
        max_y = self.height + 1

        def _wire_neighbours(rows: list[list[BaseTile]]) -> None:
            # for each row
            """Link each tile to its neighbour in every direction."""
            for r in rows:
                # for each column/tile
                for tile in r:
                    # link in every direction
                    for dir, (dx, dy) in DELTAS.items():
                        nx, ny = tile.x + dx, tile.y + dy

                        if 0 <= nx <= max_x and 0 <= ny <= max_y:
                            tile.neighbours[dir] = rows[ny][nx]

        def is_edge(x, y) -> bool:
            """True if grid position (x, y) is on the border ring."""
            return x == 0 or x == max_x or y == 0 or y == max_y

        def make_tile(x: int, y: int) -> BaseTile:
            """Create the right kind of tile for grid position (x, y)."""
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

    def __repr__(self) -> str:
        """ASCII view: S/E = entry/exit, . = solution, # = logo."""
        lines: list[str] = []
        for row in self.grid[1:-1]:
            cells = row[1:-1]
            lines.append("".join(
                "+--" if t.walls["N"] else "+  " for t in cells) + "+")
            line = ""
            for t in cells:
                if t is self._start:
                    mark = "S"
                elif t is self._goal:
                    mark = "E"
                elif t.isLogo:
                    mark = "#"
                elif t.isSolution:
                    mark = "."
                else:
                    mark = " "
                line += ("|" if t.walls["W"] else " ") + mark + " "
            lines.append(line + ("|" if cells[-1].walls["E"] else " "))
        lines.append("".join(
            "+--" if t.walls["S"] else "+  "
            for t in self.grid[-2][1:-1]) + "+")
        return "\n".join(lines)

    def _carve(self, algo: Callable[[Maze, BaseTile, bool], None]) -> None:
        """Run the carving algorithm algo, starting from the entry."""
        return algo(self, self._start, self.is_perfect)

    @property
    def entry(self) -> BaseTile:
        """Entry tile. Its x/y are grid coordinates (subtract 1 for the
        coordinates used in the config and output file)."""
        return self._start

    @property
    def exit(self) -> BaseTile:
        """Exit tile (same coordinate convention as `entry`)."""
        return self._goal

    def resolve(self) -> list[BaseTile]:
        """Find the shortest path from entry to exit with the chosen solver.

        Marks every tile of the path with `isSolution = True`.

        Returns:
            The path as a list of tiles, from entry to exit (both included).

        Raises:
            MazeErr: if no path exists.
        """
        path: list[BaseTile] | None = None
        if self._solver == "astar":
            path = astar(self._start, self._goal)
        else:
            path = bfs(self._start, self._goal)

        if path is None:
            raise MazeErr("No path between starting point and end point")
        for t in path:
            t.isSolution = True
        return path
