"""
Day 20 - Networking
Task: UDP heartbeat monitor with liveness detection and retry logic (variant 20)
"""

from __future__ import annotations
import argparse
import socket
import threading
import time


def run_server(host: str, port: int, stop: threading.Event) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        s.settimeout(0.2)
        while not stop.is_set():
            try:
                data, addr = s.recvfrom(1024)
            except socket.timeout:
                continue
            if data == b"PING":
                s.sendto(b"PONG", addr)


def monitor(host: str, port: int, attempts: int, timeout: float) -> None:
    misses = 0
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        for _ in range(attempts):
            s.sendto(b"PING", (host, port))
            try:
                data, _ = s.recvfrom(1024)
                if data == b"PONG":
                    print("heartbeat ok")
                    misses = 0
            except socket.timeout:
                misses += 1
                print("heartbeat miss", misses)
                if misses >= 3:
                    print("node unhealthy")
                    return
            time.sleep(0.2)
    print("monitor finished")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9200)
    args = parser.parse_args()
    stop = threading.Event()
    t = threading.Thread(target=run_server, args=("127.0.0.1", args.port, stop), daemon=True)
    t.start()
    time.sleep(0.1)
    monitor("127.0.0.1", args.port, attempts=10, timeout=0.15)
    stop.set()
    t.join(timeout=0.5)


if __name__ == "__main__":
    main()
