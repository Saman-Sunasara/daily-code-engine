"""
Day 2 - Game Features
Task: Expand movement into platform physics and add combat interactions (projectile vs enemies).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set, Tuple


@dataclass
class Vec2:
    x: float
    y: float


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
    def __init__(self, width: int, height: int, solids: Set[Tuple[int, int]]) -> None:
        self.width = width
        self.height = height
        self.solids = solids

    def tile_rects_near(self, rect: Rect) -> List[Rect]:
        min_x = max(0, int(rect.x) - 1)
        max_x = min(self.width - 1, int(rect.x + rect.w) + 1)
        min_y = max(0, int(rect.y) - 1)
        max_y = min(self.height - 1, int(rect.y + rect.h) + 1)
        out: List[Rect] = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if (x, y) in self.solids:
                    out.append(Rect(x, y, 1.0, 1.0))
        return out


@dataclass
class Enemy:
    hitbox: Rect
    health: int

    @property
    def alive(self) -> bool:
        return self.health > 0

    def apply_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)


@dataclass
class Projectile:
    hitbox: Rect
    velocity: Vec2
    damage: int = 1
    active: bool = True

    def update(self, dt: float) -> None:
        self.hitbox = self.hitbox.moved(self.velocity.x * dt, self.velocity.y * dt)


@dataclass
class Player:
    hitbox: Rect
    velocity: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    on_ground: bool = False
    move_accel: float = 24.0
    max_speed: float = 6.0
    gravity: float = 22.0
    jump_speed: float = 9.0
    friction: float = 10.0

    def update(self, move_input: float, jump_pressed: bool, dt: float, world: TileWorld) -> None:
        self.velocity.x += move_input * self.move_accel * dt
        self.velocity.x = max(-self.max_speed, min(self.max_speed, self.velocity.x))
        if move_input == 0.0:
            self.velocity.x = approach_zero(self.velocity.x, self.friction * dt)

        self.velocity.y += self.gravity * dt
        if jump_pressed and self.on_ground:
            self.velocity.y = -self.jump_speed
            self.on_ground = False

        self._move(world, dt)

    def _move(self, world: TileWorld, dt: float) -> None:
        self.on_ground = False
        dx = self.velocity.x * dt
        moved_x = self.hitbox.moved(dx, 0.0)
        for tile in world.tile_rects_near(moved_x):
            if intersects(moved_x, tile):
                if dx > 0:
                    moved_x.x = tile.x - moved_x.w
                elif dx < 0:
                    moved_x.x = tile.x + tile.w
                self.velocity.x = 0.0
        self.hitbox = moved_x

        dy = self.velocity.y * dt
        moved_y = self.hitbox.moved(0.0, dy)
        for tile in world.tile_rects_near(moved_y):
            if intersects(moved_y, tile):
                if dy > 0:
                    moved_y.y = tile.y - moved_y.h
                    self.on_ground = True
                elif dy < 0:
                    moved_y.y = tile.y + tile.h
                self.velocity.y = 0.0
        self.hitbox = moved_y

        # Keep player in map bounds.
        if self.hitbox.x < 0:
            self.hitbox.x = 0
            self.velocity.x = 0
        if self.hitbox.x + self.hitbox.w > world.width:
            self.hitbox.x = world.width - self.hitbox.w
            self.velocity.x = 0
        if self.hitbox.y + self.hitbox.h > world.height:
            self.hitbox.y = world.height - self.hitbox.h
            self.velocity.y = 0
            self.on_ground = True


def approach_zero(value: float, delta: float) -> float:
    if value > 0:
        return max(0.0, value - delta)
    if value < 0:
        return min(0.0, value + delta)
    return 0.0


class GameSimulation:
    def __init__(self, world: TileWorld, player: Player, enemies: List[Enemy]) -> None:
        self.world = world
        self.player = player
        self.enemies = enemies
        self.projectiles: List[Projectile] = []

    def fire_projectile(self, direction: int) -> None:
        spawn_x = self.player.hitbox.x + (self.player.hitbox.w if direction > 0 else -0.2)
        spawn_y = self.player.hitbox.y + self.player.hitbox.h * 0.5
        self.projectiles.append(
            Projectile(hitbox=Rect(spawn_x, spawn_y, 0.2, 0.2), velocity=Vec2(9.0 * direction, 0.0), damage=2)
        )

    def step(self, move_input: float, jump_pressed: bool, shoot: bool, dt: float) -> None:
        self.player.update(move_input, jump_pressed, dt, self.world)
        if shoot:
            direction = 1 if move_input >= 0 else -1
            self.fire_projectile(direction)

        for projectile in self.projectiles:
            if not projectile.active:
                continue
            projectile.update(dt)

            # Deactivate when hitting world bounds or solid tiles.
            if (
                projectile.hitbox.x < 0
                or projectile.hitbox.x > self.world.width
                or projectile.hitbox.y < 0
                or projectile.hitbox.y > self.world.height
            ):
                projectile.active = False
                continue
            for tile in self.world.tile_rects_near(projectile.hitbox):
                if intersects(projectile.hitbox, tile):
                    projectile.active = False
                    break
            if not projectile.active:
                continue

            for enemy in self.enemies:
                if enemy.alive and intersects(projectile.hitbox, enemy.hitbox):
                    enemy.apply_damage(projectile.damage)
                    projectile.active = False
                    break

        self.projectiles = [p for p in self.projectiles if p.active]


def main() -> None:
    solids = {(x, 7) for x in range(14)} | {(6, 6), (6, 5)}
    world = TileWorld(width=14, height=8, solids=solids)
    player = Player(hitbox=Rect(1.0, 6.0, 0.8, 0.8))
    enemies = [Enemy(hitbox=Rect(9.5, 6.0, 0.8, 0.8), health=4), Enemy(hitbox=Rect(12.0, 6.0, 0.8, 0.8), health=3)]
    sim = GameSimulation(world, player, enemies)
    dt = 1.0 / 20.0

    # Input timeline: run right, jump over obstacle, then shoot.
    for frame in range(1, 81):
        move = 1.0 if frame <= 55 else 0.0
        jump = frame == 18
        shoot = frame in {46, 50, 54, 60}
        sim.step(move, jump, shoot, dt)

        if frame % 10 == 0:
            hp = [enemy.health for enemy in sim.enemies]
            print(
                f"Frame {frame:02d} pos=({sim.player.hitbox.x:.2f},{sim.player.hitbox.y:.2f}) "
                f"vel=({sim.player.velocity.x:.2f},{sim.player.velocity.y:.2f}) "
                f"on_ground={sim.player.on_ground} enemy_hp={hp} active_projectiles={len(sim.projectiles)}"
            )

    print("Final enemy states:", [enemy.health for enemy in sim.enemies])


if __name__ == "__main__":
    main()
