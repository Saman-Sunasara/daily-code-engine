"""
Day 2 - Networking
Task: Reliable UDP with Go-Back-N sliding window, cumulative ACK, retries, and FIN handshake.

Examples:
  python networking.py server --port 9100 --drop-rate 0.15
  python networking.py client --port 9100 --messages alpha beta gamma --window-size 4
  python networking.py self-test --drop-rate 0.2
"""

from __future__ import annotations

import argparse
import json
import random
import socket
import threading
import time
import zlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


def checksum(content: str) -> int:
    return zlib.crc32(content.encode("utf-8")) & 0xFFFFFFFF


def make_packet(kind: str, seq: int, ack: int = -1, payload: str = "") -> bytes:
    body = {"type": kind, "seq": seq, "ack": ack, "payload": payload}
    body["checksum"] = checksum(f"{kind}|{seq}|{ack}|{payload}")
    return json.dumps(body).encode("utf-8")


def parse_packet(raw: bytes) -> Dict:
    packet = json.loads(raw.decode("utf-8"))
    expected = checksum(
        f"{packet.get('type')}|{packet.get('seq')}|{packet.get('ack')}|{packet.get('payload', '')}"
    )
    if packet.get("checksum") != expected:
        raise ValueError("Checksum mismatch")
    return packet


@dataclass
class ReliableUDPReceiver:
    host: str
    port: int
    drop_rate: float = 0.0
    timeout: float = 0.8

    def serve(self, stop_event: Optional[threading.Event] = None) -> List[str]:
        delivered: List[str] = []
        expected_seq = 0
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.port))
            sock.settimeout(self.timeout)
            print(f"Receiver listening on {self.host}:{self.port}")

            while True:
                if stop_event and stop_event.is_set():
                    break

                try:
                    raw, sender = sock.recvfrom(4096)
                except socket.timeout:
                    continue

                if random.random() < self.drop_rate:
                    # Simulate network loss.
                    continue

                try:
                    packet = parse_packet(raw)
                except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                    continue

                ptype = packet.get("type")
                seq = int(packet.get("seq", -1))

                if ptype == "DATA":
                    payload = packet.get("payload", "")
                    if seq == expected_seq:
                        delivered.append(payload)
                        expected_seq += 1
                        print(f"Accepted seq={seq}: {payload}")
                    else:
                        print(f"Out-of-order seq={seq}, expected={expected_seq}")

                    ack_packet = make_packet("ACK", seq=-1, ack=expected_seq - 1)
                    if random.random() >= self.drop_rate:
                        sock.sendto(ack_packet, sender)
                    continue

                if ptype == "FIN":
                    fin_ack = make_packet("FIN_ACK", seq=-1, ack=expected_seq - 1)
                    sock.sendto(fin_ack, sender)
                    print("FIN received. Closing receiver.")
                    break

        return delivered


@dataclass
class ReliableUDPSender:
    host: str
    port: int
    window_size: int = 4
    timeout: float = 0.5
    max_retries: int = 12

    def send(self, messages: List[str]) -> None:
        address = (self.host, self.port)
        packets = [make_packet("DATA", seq=i, payload=msg) for i, msg in enumerate(messages)]
        base = 0
        next_seq = 0
        retries: Dict[int, int] = {i: 0 for i in range(len(messages))}

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)
            while base < len(packets):
                while next_seq < base + self.window_size and next_seq < len(packets):
                    sock.sendto(packets[next_seq], address)
                    next_seq += 1

                try:
                    raw_ack, _ = sock.recvfrom(4096)
                    ack = parse_packet(raw_ack)
                    if ack.get("type") != "ACK":
                        continue
                    ack_no = int(ack.get("ack", -1))
                    if ack_no >= base:
                        base = ack_no + 1
                except (socket.timeout, TimeoutError):
                    for i in range(base, next_seq):
                        retries[i] += 1
                        if retries[i] > self.max_retries:
                            raise TimeoutError(f"Packet seq={i} failed after max retries.")
                        sock.sendto(packets[i], address)
                except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                    continue

            # FIN handshake
            fin = make_packet("FIN", seq=len(messages))
            for _ in range(self.max_retries):
                sock.sendto(fin, address)
                try:
                    raw, _ = sock.recvfrom(4096)
                    packet = parse_packet(raw)
                    if packet.get("type") == "FIN_ACK":
                        return
                except (socket.timeout, TimeoutError, json.JSONDecodeError, UnicodeDecodeError, ValueError):
                    continue
            raise TimeoutError("FIN handshake failed.")


def run_server(args: argparse.Namespace) -> None:
    receiver = ReliableUDPReceiver(
        host=args.host,
        port=args.port,
        drop_rate=args.drop_rate,
        timeout=args.timeout,
    )
    delivered = receiver.serve()
    print(f"Delivered messages ({len(delivered)}): {delivered}")


def run_client(args: argparse.Namespace) -> None:
    sender = ReliableUDPSender(
        host=args.host,
        port=args.port,
        window_size=args.window_size,
        timeout=args.timeout,
        max_retries=args.max_retries,
    )
    started = time.time()
    sender.send(args.messages)
    print(f"Client delivered {len(args.messages)} messages in {time.time() - started:.2f}s")


def run_self_test(args: argparse.Namespace) -> None:
    messages = args.messages or [f"msg-{i}" for i in range(12)]
    stop_event = threading.Event()
    receiver = ReliableUDPReceiver(
        host="127.0.0.1",
        port=args.port,
        drop_rate=args.drop_rate,
        timeout=0.25,
    )
    results: Dict[str, List[str]] = {"delivered": []}

    def server_job() -> None:
        results["delivered"] = receiver.serve(stop_event=stop_event)

    thread = threading.Thread(target=server_job, daemon=True)
    thread.start()
    time.sleep(0.15)

    sender = ReliableUDPSender(
        host="127.0.0.1",
        port=args.port,
        window_size=args.window_size,
        timeout=0.25,
        max_retries=args.max_retries,
    )
    sender.send(messages)
    time.sleep(0.3)
    stop_event.set()
    thread.join(timeout=1.0)

    if results["delivered"] != messages:
        raise AssertionError("Self-test failed: delivered messages do not match sent messages.")
    print("Self-test passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reliable UDP Go-Back-N implementation.")
    sub = parser.add_subparsers(dest="mode", required=True)

    server = sub.add_parser("server", help="Run as receiver")
    server.add_argument("--host", default="127.0.0.1")
    server.add_argument("--port", type=int, default=9100)
    server.add_argument("--drop-rate", type=float, default=0.0)
    server.add_argument("--timeout", type=float, default=0.8)

    client = sub.add_parser("client", help="Run as sender")
    client.add_argument("--host", default="127.0.0.1")
    client.add_argument("--port", type=int, default=9100)
    client.add_argument("--messages", nargs="+", required=True)
    client.add_argument("--window-size", type=int, default=4)
    client.add_argument("--timeout", type=float, default=0.5)
    client.add_argument("--max-retries", type=int, default=12)

    test = sub.add_parser("self-test", help="Run local sender/receiver validation")
    test.add_argument("--port", type=int, default=9101)
    test.add_argument("--messages", nargs="*")
    test.add_argument("--drop-rate", type=float, default=0.15)
    test.add_argument("--window-size", type=int, default=4)
    test.add_argument("--max-retries", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "server":
        run_server(args)
    elif args.mode == "client":
        run_client(args)
    else:
        run_self_test(args)


if __name__ == "__main__":
    main()
