import heapq
from tiles import BaseTile
from dirs import DIRS
from collections import deque


def astar(start: BaseTile, goal: BaseTile) -> list[BaseTile] | None:
    def h(t: BaseTile) -> int:
        return abs(t.x - goal.x) + abs(t.y - goal.y)

    open_: list[tuple[int, BaseTile]] = [(h(start), start)]
    came: dict[BaseTile, BaseTile | None] = {start: None}
    cost: dict[BaseTile, int] = {start: 0}
    closed: set[BaseTile] = set()

    while open_:
        _, cur = heapq.heappop(open_)
        if cur is goal:
            path: list[BaseTile] = []
            node: BaseTile | None = cur
            while node is not None:
                path.append(node)
                node = came[node]
            return path[::-1]

        if cur in closed:            # stale duplicate entry from an earlier push
            continue
        closed.add(cur)

        for d in DIRS:
            nxt = cur.goto(d)
            if not nxt:
                continue
            c = cost[cur] + 1
            if nxt not in cost or c < cost[nxt]:
                cost[nxt] = c
                came[nxt] = cur
                heapq.heappush(open_, (c + h(nxt), nxt))
    return None

def bfs(start: BaseTile, goal: BaseTile) -> list[BaseTile] | None:
    """Return the shortest path from start to goal, or None if unreachable.

    Every move costs 1, so the first time BFS reaches a tile,
    it has reached it by a shortest path.
    """
    queue: deque[BaseTile] = deque([start])
    came: dict[BaseTile, BaseTile | None] = {start: None}

    while queue:
        cur = queue.popleft()            # oldest tile = closest to start
        if cur is goal:
            path: list[BaseTile] = []
            node: BaseTile | None = cur
            while node is not None:      # walk back to start via `came`
                path.append(node)
                node = came[node]
            return path[::-1]

        for d in DIRS:
            nxt = cur.goto(d)            # False if a wall blocks the way
            if not nxt or nxt in came:   # wall, or already discovered
                continue
            came[nxt] = cur              # remember where we came from
            queue.append(nxt)
    return None
