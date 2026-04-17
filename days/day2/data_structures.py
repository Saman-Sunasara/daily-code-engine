"""
Day 2 - Data Structures & Algorithms
Task: A* pathfinding on a weighted grid with obstacle support.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple


Point = Tuple[int, int]


@dataclass(frozen=True)
class GridConfig:
    width: int
    height: int
    allow_diagonal: bool = False


class WeightedGrid:
    """2D grid with per-cell movement cost and blocked cells."""

    def __init__(
        self,
        config: GridConfig,
        blocked: Optional[set[Point]] = None,
        terrain_cost: Optional[Dict[Point, int]] = None,
    ) -> None:
        self.config = config
        self.blocked = blocked or set()
        self.terrain_cost = terrain_cost or {}

    def in_bounds(self, p: Point) -> bool:
        x, y = p
        return 0 <= x < self.config.width and 0 <= y < self.config.height

    def passable(self, p: Point) -> bool:
        return p not in self.blocked

    def cost(self, p: Point) -> int:
        return self.terrain_cost.get(p, 1)

    def neighbors(self, p: Point) -> Iterable[Point]:
        x, y = p
        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if self.config.allow_diagonal:
            offsets += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in offsets:
            nxt = (x + dx, y + dy)
            if self.in_bounds(nxt) and self.passable(nxt):
                yield nxt


def heuristic(a: Point, b: Point, diagonal: bool) -> int:
    ax, ay = a
    bx, by = b
    dx = abs(ax - bx)
    dy = abs(ay - by)
    return max(dx, dy) if diagonal else dx + dy


def reconstruct_path(parent: Dict[Point, Optional[Point]], goal: Point) -> List[Point]:
    out: List[Point] = []
    cur: Optional[Point] = goal
    while cur is not None:
        out.append(cur)
        cur = parent[cur]
    out.reverse()
    return out


def a_star(grid: WeightedGrid, start: Point, goal: Point) -> Tuple[int, List[Point]]:
    if not grid.in_bounds(start) or not grid.in_bounds(goal):
        raise ValueError("Start and goal must be inside the grid.")
    if not grid.passable(start) or not grid.passable(goal):
        raise ValueError("Start and goal must be passable cells.")

    open_heap: List[Tuple[int, int, Point]] = []
    g_cost: Dict[Point, int] = {start: 0}
    parent: Dict[Point, Optional[Point]] = {start: None}

    tie_breaker = 0
    start_h = heuristic(start, goal, grid.config.allow_diagonal)
    heapq.heappush(open_heap, (start_h, tie_breaker, start))

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current == goal:
            return g_cost[current], reconstruct_path(parent, goal)

        for nxt in grid.neighbors(current):
            cand = g_cost[current] + grid.cost(nxt)
            if cand < g_cost.get(nxt, 10**12):
                g_cost[nxt] = cand
                parent[nxt] = current
                tie_breaker += 1
                f_cost = cand + heuristic(nxt, goal, grid.config.allow_diagonal)
                heapq.heappush(open_heap, (f_cost, tie_breaker, nxt))

    return -1, []


def render_path(width: int, height: int, blocked: set[Point], path: List[Point]) -> str:
    path_set = set(path)
    lines: List[str] = []
    for y in range(height):
        row = []
        for x in range(width):
            p = (x, y)
            if p in blocked:
                row.append("#")
            elif p in path_set:
                row.append("*")
            else:
                row.append(".")
        lines.append("".join(row))
    return "\n".join(lines)


def main() -> None:
    blocked = {(3, 0), (3, 1), (3, 2), (3, 4), (5, 3), (6, 3)}
    terrain_cost = {(1, 3): 3, (2, 3): 3, (4, 3): 3, (5, 4): 4}
    grid = WeightedGrid(GridConfig(width=10, height=6, allow_diagonal=False), blocked, terrain_cost)
    start, goal = (0, 0), (9, 5)

    cost, path = a_star(grid, start, goal)
    if not path:
        print("No path found.")
        return

    print(f"Path cost: {cost}")
    print(f"Path length: {len(path)}")
    print("Path:", path)
    print(render_path(grid.config.width, grid.config.height, blocked, path))


if __name__ == "__main__":
    main()
