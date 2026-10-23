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


def reachable(start: BaseTile) -> list[BaseTile]:
    """All carvable tiles connected to start, ignoring walls.
    Returned in deterministic BFS order."""
    seen = {start}
    order = [start]
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for d in DIRS:
            nxt = cur.neighbours[d]
            if carvable(nxt) and nxt not in seen:
                assert nxt is not None
                seen.add(nxt)
                order.append(nxt)
                queue.append(nxt)
    return order
