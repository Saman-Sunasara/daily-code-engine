"""
Day 20 - Data Structures & Algorithms
Task: Union-Find + Kruskal minimum spanning tree (variant 20)
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Edge:
    u: str
    v: str
    w: int


class DSU:
    def __init__(self, nodes: list[str]) -> None:
        self.parent = {n: n for n in nodes}
        self.rank = {n: 0 for n in nodes}

    def find(self, x: str) -> str:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: str, b: str) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal(nodes: list[str], edges: list[Edge]) -> tuple[int, list[Edge]]:
    dsu = DSU(nodes)
    total = 0
    mst: list[Edge] = []
    for e in sorted(edges, key=lambda x: x.w):
        if dsu.union(e.u, e.v):
            total += e.w
            mst.append(e)
    return total, mst


def main() -> None:
    nodes = ["A", "B", "C", "D", "E"]
    edges = [
        Edge("A", "B", 1), Edge("A", "C", 3), Edge("B", "C", 2),
        Edge("B", "D", 4), Edge("C", "D", 5), Edge("C", "E", 6), Edge("D", "E", 7)
    ]
    total, mst = kruskal(nodes, edges)
    print("MST total:", total)
    print("Edges:", [(e.u, e.v, e.w) for e in mst])


if __name__ == "__main__":
    main()
