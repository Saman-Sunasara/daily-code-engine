"""
Day 14 - Game Features
Task: Event-driven combat loop with cooldown system (variant 14)
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Event:
    kind: str
    value: int


class EventBus:
    def __init__(self) -> None:
        self.queue: list[Event] = []

    def emit(self, e: Event) -> None:
        self.queue.append(e)

    def drain(self) -> list[Event]:
        out = self.queue[:]
        self.queue.clear()
        return out


@dataclass
class Actor:
    name: str
    hp: int
    cooldown: float = 0.0

    def update(self, dt: float) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)

    def try_attack(self, bus: EventBus, dmg: int) -> None:
        if self.cooldown == 0.0:
            bus.emit(Event("damage", dmg))
            self.cooldown = 0.6


def main() -> None:
    bus = EventBus()
    enemy = Actor("enemy", 18)
    player = Actor("player", 30)
    dt = 0.2
    for tick in range(1, 31):
        player.update(dt)
        enemy.update(dt)
        player.try_attack(bus, 2)
        if tick % 6 == 0:
            enemy.try_attack(bus, 3)

        for e in bus.drain():
            if e.kind == "damage":
                if tick % 6 == 0:
                    player.hp -= e.value
                else:
                    enemy.hp -= e.value
        if tick % 5 == 0:
            print(f"tick={tick} player_hp={player.hp} enemy_hp={enemy.hp}")
        if player.hp <= 0 or enemy.hp <= 0:
            break


if __name__ == "__main__":
    main()
