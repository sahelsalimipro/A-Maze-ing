from collections import deque
from tiles import BaseTile
from dirs import DIRS, OPP_DIR, Direction


def carvable(t: BaseTile | None) -> bool:
    return t is not None and not t.isLimit and not t.isLogo


def carve(tile: BaseTile, d: Direction) -> None:
    other = tile.neighbours[d]
    assert other is not None
    tile.walls[d] = False
    other.walls[OPP_DIR[d]] = False
    tile.wallscount -= 1
    other.wallscount -= 1


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