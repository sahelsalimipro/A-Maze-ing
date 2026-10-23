import heapq
from tiles import BaseTile
from dirs import DIRS


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
