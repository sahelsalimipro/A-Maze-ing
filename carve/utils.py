from __future__ import annotations
from typing import TypeGuard, TYPE_CHECKING
from collections import deque
from tiles import BaseTile
from dirs import DIRS, OPP_DIR, Direction

if TYPE_CHECKING:
    from random import Random

def carvable(t: BaseTile | None) -> TypeGuard[BaseTile]:
    return t is not None and not t.isLimit and not t.isLogo

def carve(tile: BaseTile, d: Direction) -> None:
    """Opens the wall between tile and its neighbour d."""

    other = tile.neighbours[d]
    assert other is not None
    tile.walls[d] = False
    other.walls[OPP_DIR[d]] = False
    tile.wallscount -= 1
    other.wallscount -= 1

def uncarve(tile: BaseTile, d: Direction) -> None:
    """Close the wall between tile and its neighbour d (undo carve)."""

    other = tile.neighbours[d]
    assert other is not None
    tile.walls[d] = True
    other.walls[OPP_DIR[d]] = True
    tile.wallscount += 1
    other.wallscount += 1

def find_components(
    grid: list[list[BaseTile]],
) -> tuple[list[list[BaseTile]], dict[BaseTile, int]]:
    """Connected groups of carvable tiles (walls ignored), computed in one pass.
    Returns (components, component_of): the tiles of each component, and tile -> component index.
    Grid order makes it deterministic."""
    components: list[list[BaseTile]] = []
    component_of: dict[BaseTile, int] = {}

    for row in grid:
        for tile in row:
            if not carvable(tile) or tile in component_of:
                continue
            idx = len(components)
            members = [tile]
            component_of[tile] = idx
            queue = deque([tile])
            while queue:
                cur = queue.popleft()
                for d in DIRS:
                    nxt = cur.neighbours[d]
                    if nxt is not None and carvable(nxt) and nxt not in component_of:
                        component_of[nxt] = idx
                        members.append(nxt)
                        queue.append(nxt)
            components.append(members)

    return components, component_of

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# |                   BRAIDING                                 >
# /////////////////////////////////////////////////////////////

def braid(rng: Random, cells: list[BaseTile]) -> None:
    """Remove every dead end without creating any 2x2 open area.

    Open one closed wall of a dead end. If that completes a 2x2 open
    square, close another wall of that square. This can leave a new dead
    end next to it, which a later step fixes: dead ends "walk" until two
    of them meet and cancel out. Cells that the logo leaves with a single
    neighbour cannot be fixed and stay dead ends.
    """
    forced = {t for t in cells if _count_carvable_neighbours(t) == 1}
    for _ in range(40 * len(cells)):        # safety limit, never reached
        dead = [t for t in cells if _is_dead_end(t) and t not in forced]
        if not dead:
            return
        t = rng.choice(dead)
        closed: list[Direction] = [d for d in DIRS if t.walls[d] and carvable(t.neighbours[d])]
        joins: list[Direction] = [d for d in closed if _is_dead_end(t.neighbours[d])]
        d: Direction = rng.choice(joins or closed)     # prefer joining two dead ends
        n = t.neighbours[d]
        assert n is not None
        carve(t, d)
        _break_squares(rng, t, n)


def _count_carvable_neighbours(t: BaseTile) -> int:
    """How many neighbours of t could ever be connected to it."""
    return sum(1 for d in DIRS if carvable(t.neighbours[d]))


def _is_dead_end(t: BaseTile | None) -> bool:
    """True if t is a tile with exactly one open wall."""
    return t is not None and t.wallscount == 3


def _break_squares(rng: Random, t: BaseTile, n: BaseTile) -> None:
    """Close walls until no 2x2 open square contains t or n.

    The wall t-n that was just opened is never closed again.
    """
    while True:
        squares = _open_squares(t) + _open_squares(n)
        if not squares:
            return
        walls: list[tuple[BaseTile, Direction]] = [
            (u, e) for (u, e) in _square_walls(squares[0])
            if {u, u.neighbours[e]} != {t, n}
        ]
        safe: list[tuple[BaseTile, Direction]] = [
            (u, e) for (u, e) in walls
            if _closing_is_safe(u, e)
        ]
        u, e = rng.choice(safe or walls)
        uncarve(u, e)


def _closing_is_safe(u: BaseTile, e: Direction) -> bool:
    """True if closing the wall u-e leaves both tiles with 2+ openings."""
    v = u.neighbours[e]
    return v is not None and u.wallscount <= 1 and v.wallscount <= 1


def _open_squares(t: BaseTile) -> list[BaseTile]:
    """Top-left tiles of every 2x2 open square that contains t."""
    grid = t.maze_ref.grid
    corners = [grid[y][x] for y in (t.y - 1, t.y) for x in (t.x - 1, t.x)]
    return [a for a in corners if _is_open_square(a)]


def _is_open_square(a: BaseTile) -> bool:
    """True if a, its E, S and SE neighbours have no wall between them."""
    b, c = a.neighbours["E"], a.neighbours["S"]
    if not (carvable(a) and carvable(b) and carvable(c)):
        return False
    return (carvable(b.neighbours["S"])
            and not a.walls["E"] and not a.walls["S"]
            and not b.walls["S"] and not c.walls["E"])


def _square_walls(a: BaseTile) -> list[tuple[BaseTile, Direction]]:
    """The 4 inner walls of the 2x2 square whose top-left tile is a."""
    b, c = a.neighbours["E"], a.neighbours["S"]
    assert b is not None and c is not None
    return [(a, "E"), (a, "S"), (b, "S"), (c, "E")]
