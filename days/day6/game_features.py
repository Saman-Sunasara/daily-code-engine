"""
Day 6 - Game Features
Task: Spatial-hash broad-phase collision detection (variant 6)
"""

from __future__ import annotations
from dataclasses import dataclass
import random


@dataclass
class Body:
    x: float
    y: float
    r: float


def key(x: float, y: float, cell: float) -> tuple[int, int]:
    return int(x // cell), int(y // cell)


def detect_collisions(bodies: list[Body], cell: float = 1.0) -> int:
    grid: dict[tuple[int, int], list[int]] = {}
    for i, b in enumerate(bodies):
        grid.setdefault(key(b.x, b.y, cell), []).append(i)

    collisions = 0
    for ids in grid.values():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a = bodies[ids[i]]
                b = bodies[ids[j]]
                if (a.x - b.x) ** 2 + (a.y - b.y) ** 2 <= (a.r + b.r) ** 2:
                    collisions += 1
    return collisions


def main() -> None:
    random.seed(7)
    bodies = [Body(random.random() * 10, random.random() * 10, 0.25) for _ in range(200)]
    print("Collisions:", detect_collisions(bodies, cell=0.8))


if __name__ == "__main__":
    main()
