"""
Day 12 - Networking
Task: AIMD congestion-control simulation with packet-loss response (variant 12)
"""

from __future__ import annotations
import argparse
import random


def aimd_rounds(rounds: int, loss_rate: float) -> list[float]:
    cwnd = 1.0
    history = []
    for _ in range(rounds):
        loss = random.random() < loss_rate
        if loss:
            cwnd = max(1.0, cwnd / 2.0)
        else:
            cwnd += 1.0 / cwnd
        history.append(round(cwnd, 3))
    return history


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=25)
    parser.add_argument("--loss-rate", type=float, default=0.15)
    args = parser.parse_args()
    hist = aimd_rounds(args.rounds, args.loss_rate)
    print("Final cwnd:", hist[-1])
    print("Sample:", hist[:10], "...")


if __name__ == "__main__":
    main()
