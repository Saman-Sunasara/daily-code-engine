"""
Day 1 - Data Structures & Algorithms
Task: Implement Dijkstra's shortest path with path reconstruction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import heapq
from typing import Dict, List, Tuple


@dataclass
class WeightedGraph:
    """Simple adjacency-list graph for weighted directed/undirected edges."""

    adjacency: Dict[str, List[Tuple[str, int]]] = field(default_factory=dict)

    def add_edge(self, u: str, v: str, w: int, bidirectional: bool = True) -> None:
        if w < 0:
            raise ValueError("Dijkstra requires non-negative edge weights.")
        self.adjacency.setdefault(u, []).append((v, w))
        self.adjacency.setdefault(v, [])
        if bidirectional:
            self.adjacency[v].append((u, w))

    def dijkstra(self, start: str, target: str) -> Tuple[int, List[str]]:
        if start not in self.adjacency or target not in self.adjacency:
            raise KeyError("Both start and target nodes must exist in the graph.")

        distance: Dict[str, int] = {node: float("inf") for node in self.adjacency}
        previous: Dict[str, str | None] = {node: None for node in self.adjacency}
        distance[start] = 0

        min_heap: List[Tuple[int, str]] = [(0, start)]
        while min_heap:
            current_dist, node = heapq.heappop(min_heap)
            if current_dist > distance[node]:
                continue
            if node == target:
                break

            for neighbor, edge_weight in self.adjacency[node]:
                candidate_dist = current_dist + edge_weight
                if candidate_dist < distance[neighbor]:
                    distance[neighbor] = candidate_dist
                    previous[neighbor] = node
                    heapq.heappush(min_heap, (candidate_dist, neighbor))

        if distance[target] == float("inf"):
            return float("inf"), []

        path = self._reconstruct_path(previous, target)
        return distance[target], path

    @staticmethod
    def _reconstruct_path(previous: Dict[str, str | None], target: str) -> List[str]:
        path: List[str] = []
        cursor: str | None = target
        while cursor is not None:
            path.append(cursor)
            cursor = previous[cursor]
        path.reverse()
        return path


def build_sample_graph() -> WeightedGraph:
    g = WeightedGraph()
    g.add_edge("A", "B", 4)
    g.add_edge("A", "C", 2)
    g.add_edge("B", "C", 1)
    g.add_edge("B", "D", 5)
    g.add_edge("C", "D", 8)
    g.add_edge("C", "E", 10)
    g.add_edge("D", "E", 2)
    g.add_edge("D", "F", 6)
    g.add_edge("E", "F", 3)
    return g


def main() -> None:
    graph = build_sample_graph()
    start, target = "A", "F"
    dist, path = graph.dijkstra(start, target)
    print(f"Shortest distance {start} -> {target}: {dist}")
    print("Path:", " -> ".join(path))


if __name__ == "__main__":
    main()
