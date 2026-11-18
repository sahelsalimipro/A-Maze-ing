from __future__ import annotations
from collections.abc import Callable
from random import Random

from .tiles import BaseTile, Tile, Limit, LogoTile
from .dirs import DELTAS
from .carve import pick_endpoints, wilson, find_components, dfs
from .solvers import astar, bfs
from .errors import MazeErr


LOGO_42: tuple[str, ...] = (
    "#...###",
    "#.....#",
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


class Maze():
    def __init__(
        self, width, height,
        seed=None, perfect=True,
        entry=None, exit=None,
        carver="dfs", solver="bfs"
    ) -> None:

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
        return algo(self, self._start, self.is_perfect)

    def resolve(self) -> None:
        path: list[BaseTile] | None = None
        if self._solver == "astar":
            path = astar(self._start, self._goal)
        else:
            path = bfs(self._start, self._goal)

        if path is None:
            raise MazeErr("No path between starting point and end point")
        for t in path:
            t.isSolution = True
        return
