"""
Day 13 - Networking
Task: Selective repeat reliability simulation with out-of-order buffering (variant 13)
"""

from __future__ import annotations
import argparse
import random


def selective_repeat_sim(messages: list[str], window_size: int, drop_rate: float, seed: int = 42) -> list[str]:
    random.seed(seed)
    n = len(messages)
    sent = 0
    base = 0
    acked = [False] * n
    recv_buffer: dict[int, str] = {}
    delivered: list[str] = []

    while base < n:
        while sent < n and sent < base + window_size:
            if random.random() >= drop_rate:
                recv_buffer[sent] = messages[sent]
            sent += 1

        for seq in sorted(recv_buffer):
            acked[seq] = True
        while base < n and acked[base]:
            delivered.append(messages[base])
            base += 1
        for seq in range(base, sent):
            if not acked[seq] and random.random() >= drop_rate:
                recv_buffer[seq] = messages[seq]
    return delivered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=int, default=4)
    parser.add_argument("--drop-rate", type=float, default=0.25)
    args = parser.parse_args()
    msgs = [f"pkt-{i}" for i in range(12)]
    out = selective_repeat_sim(msgs, args.window, args.drop_rate)
    print("Delivered all:", out == msgs)
    print("Count:", len(out))


if __name__ == "__main__":
    main()
