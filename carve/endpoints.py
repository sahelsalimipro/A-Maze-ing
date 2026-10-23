from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amazeing import Maze
    from tiles import BaseTile
from .utils import reachable, carvable

def pick_endpoints(maze: Maze) -> tuple[BaseTile, BaseTile]:
    rng = maze._rng

    def on_border(t: BaseTile) -> bool:
        return t.x in (1, maze.width) or t.y in (1, maze.height)

    border = [t for row in maze.grid for t in row
              if carvable(t) and on_border(t)]
    if not border:
        raise ValueError("No valid border tile for the entry")

    entry = rng.choice(border)

    # The exit must be on the border AND in the same region as the entry
    region = set(reachable(entry))
    candidates = [t for t in border if t in region and t is not entry]
    if not candidates:
        raise ValueError("No valid exit reachable from the entry")

    return entry, rng.choice(candidates)
