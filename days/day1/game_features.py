"""
Day 1 - Game Features
Task: Player movement + collision resolution against a tile world.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Set, Tuple


@dataclass
class Vec2:
    x: float
    y: float

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> "Vec2":
        return Vec2(self.x * scalar, self.y * scalar)


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    def moved(self, dx: float, dy: float) -> "Rect":
        return Rect(self.x + dx, self.y + dy, self.w, self.h)


def intersects(a: Rect, b: Rect) -> bool:
    return not (
        a.x + a.w <= b.x
        or b.x + b.w <= a.x
        or a.y + a.h <= b.y
        or b.y + b.h <= a.y
    )


class TileWorld:
    """Grid world where blocked tiles are treated as axis-aligned colliders."""

    def __init__(self, width: int, height: int, blocked_tiles: Set[Tuple[int, int]]) -> None:
        self.width = width
        self.height = height
        self.blocked_tiles = blocked_tiles

    def colliders_near(self, rect: Rect) -> Iterable[Rect]:
        min_x = max(0, int(rect.x) - 1)
        max_x = min(self.width - 1, int(rect.x + rect.w) + 1)
        min_y = max(0, int(rect.y) - 1)
        max_y = min(self.height - 1, int(rect.y + rect.h) + 1)
        for gy in range(min_y, max_y + 1):
            for gx in range(min_x, max_x + 1):
                if (gx, gy) in self.blocked_tiles:
                    yield Rect(gx, gy, 1.0, 1.0)


@dataclass
class Player:
    hitbox: Rect
    velocity: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    max_speed: float = 5.0
    acceleration: float = 20.0
    friction: float = 10.0

    def update(self, input_dir: Vec2, dt: float, world: TileWorld) -> None:
        # Apply acceleration based on input.
        self.velocity.x += input_dir.x * self.acceleration * dt
        self.velocity.y += input_dir.y * self.acceleration * dt

        # Clamp speed.
        self.velocity.x = max(-self.max_speed, min(self.max_speed, self.velocity.x))
        self.velocity.y = max(-self.max_speed, min(self.max_speed, self.velocity.y))

        # Apply friction when axis has no input.
        if input_dir.x == 0:
            self.velocity.x = _approach_zero(self.velocity.x, self.friction * dt)
        if input_dir.y == 0:
            self.velocity.y = _approach_zero(self.velocity.y, self.friction * dt)

        self._move_and_collide(world, dt)

    def _move_and_collide(self, world: TileWorld, dt: float) -> None:
        # Resolve X first.
        dx = self.velocity.x * dt
        moved_x = self.hitbox.moved(dx, 0.0)
        for tile in world.colliders_near(moved_x):
            if intersects(moved_x, tile):
                if dx > 0:
                    moved_x.x = tile.x - moved_x.w
                elif dx < 0:
                    moved_x.x = tile.x + tile.w
                self.velocity.x = 0.0
        if moved_x.x < 0.0:
            moved_x.x = 0.0
            self.velocity.x = 0.0
        if moved_x.x + moved_x.w > world.width:
            moved_x.x = world.width - moved_x.w
            self.velocity.x = 0.0
        self.hitbox = moved_x

        # Resolve Y second.
        dy = self.velocity.y * dt
        moved_y = self.hitbox.moved(0.0, dy)
        for tile in world.colliders_near(moved_y):
            if intersects(moved_y, tile):
                if dy > 0:
                    moved_y.y = tile.y - moved_y.h
                elif dy < 0:
                    moved_y.y = tile.y + tile.h
                self.velocity.y = 0.0
        if moved_y.y < 0.0:
            moved_y.y = 0.0
            self.velocity.y = 0.0
        if moved_y.y + moved_y.h > world.height:
            moved_y.y = world.height - moved_y.h
            self.velocity.y = 0.0
        self.hitbox = moved_y


def _approach_zero(value: float, delta: float) -> float:
    if value > 0:
        return max(0.0, value - delta)
    if value < 0:
        return min(0.0, value + delta)
    return value


def scripted_inputs() -> List[Vec2]:
    # Simple simulated input sequence: right, down, left.
    return [Vec2(1, 0)] * 20 + [Vec2(0, 1)] * 20 + [Vec2(-1, 0)] * 20


def main() -> None:
    blocked = {(3, 1), (3, 2), (3, 3), (5, 4), (6, 4)}
    world = TileWorld(10, 8, blocked)
    player = Player(Rect(1.0, 1.0, 0.8, 0.8))
    dt = 1 / 20

    for frame, inp in enumerate(scripted_inputs(), start=1):
        player.update(inp, dt, world)
        if frame % 10 == 0:
            print(
                f"Frame {frame:02d} -> pos=({player.hitbox.x:.2f}, {player.hitbox.y:.2f}) "
                f"vel=({player.velocity.x:.2f}, {player.velocity.y:.2f})"
            )


if __name__ == "__main__":
    main()
