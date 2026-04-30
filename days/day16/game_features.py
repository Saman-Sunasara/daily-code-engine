"""
Day 16 - Game Features
Task: Enemy finite-state machine with patrol/chase/attack transitions (variant 16)
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Enemy:
    x: float
    state: str = "PATROL"
    health: int = 10

    def step(self, player_x: float, dt: float) -> None:
        dist = abs(player_x - self.x)
        if self.health <= 0:
            self.state = "DEAD"
            return
        if dist < 1.0:
            self.state = "ATTACK"
        elif dist < 4.0:
            self.state = "CHASE"
        else:
            self.state = "PATROL"

        if self.state == "PATROL":
            self.x += 0.5 * dt
        elif self.state == "CHASE":
            self.x += (1.2 if player_x > self.x else -1.2) * dt


def main() -> None:
    enemy = Enemy(x=0.0)
    player_x = 5.0
    dt = 0.2
    for frame in range(1, 31):
        if frame > 18:
            player_x = 1.0
        enemy.step(player_x, dt)
        if frame % 5 == 0:
            print(f"frame={frame} state={enemy.state} enemy_x={enemy.x:.2f} player_x={player_x:.2f}")


if __name__ == "__main__":
    main()
