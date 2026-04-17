"""
Day 1 - Networking
Task: Reliable UDP messaging using sequence numbers, ACKs, retries, and checksum.

Run examples:
  Server: python networking.py server --port 9000
  Client: python networking.py client --host 127.0.0.1 --port 9000 --messages "hello" "world"
"""

from __future__ import annotations

import argparse
import json
import socket
import time
import zlib
from dataclasses import dataclass
from typing import Optional, Tuple


def _checksum(payload: str) -> int:
    return zlib.crc32(payload.encode("utf-8")) & 0xFFFFFFFF


def encode_packet(kind: str, seq: int, payload: str = "") -> bytes:
    body = {
        "type": kind,
        "seq": seq,
        "payload": payload,
        "checksum": _checksum(payload),
    }
    return json.dumps(body).encode("utf-8")


def decode_packet(raw: bytes) -> dict:
    packet = json.loads(raw.decode("utf-8"))
    expected = _checksum(packet.get("payload", ""))
    if packet.get("checksum") != expected:
        raise ValueError("Packet checksum mismatch.")
    return packet


@dataclass
class ReliableUDPSender:
    host: str
    port: int
    timeout_seconds: float = 0.75
    max_retries: int = 5

    def send_messages(self, messages: list[str]) -> None:
        address = (self.host, self.port)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout_seconds)
            seq = 0
            for msg in messages:
                packet = encode_packet("DATA", seq, msg)
                for attempt in range(1, self.max_retries + 1):
                    sock.sendto(packet, address)
                    try:
                        ack_bytes, _ = sock.recvfrom(4096)
                        ack = decode_packet(ack_bytes)
                        if ack.get("type") == "ACK" and ack.get("seq") == seq:
                            print(f"Delivered seq={seq} in attempt {attempt}")
                            seq += 1
                            break
                    except (TimeoutError, socket.timeout):
                        pass
                    except ValueError:
                        # Corrupt ACK: continue retrying.
                        pass
                    if attempt == self.max_retries:
                        raise TimeoutError(f"Failed to deliver seq={seq} after retries.")
                    print(f"Retry seq={seq}, attempt={attempt + 1}")


@dataclass
class ReliableUDPReceiver:
    host: str
    port: int
    idle_timeout: Optional[float] = None

    def serve(self) -> None:
        expected_seq = 0
        seen_payloads: list[str] = []
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.port))
            if self.idle_timeout:
                sock.settimeout(self.idle_timeout)

            print(f"Receiver listening on {self.host}:{self.port}")
            while True:
                try:
                    packet_bytes, sender_addr = sock.recvfrom(4096)
                except socket.timeout:
                    print("Idle timeout reached, stopping receiver.")
                    break

                try:
                    packet = decode_packet(packet_bytes)
                except ValueError:
                    continue

                if packet.get("type") != "DATA":
                    continue

                seq = packet.get("seq")
                payload = packet.get("payload", "")

                if seq == expected_seq:
                    seen_payloads.append(payload)
                    expected_seq += 1
                    print(f"Accepted seq={seq}: {payload}")
                else:
                    print(f"Duplicate/out-of-order packet seq={seq}, expected={expected_seq}")

                ack_seq = expected_seq - 1
                sock.sendto(encode_packet("ACK", ack_seq), sender_addr)

            print("Received messages:", seen_payloads)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reliable UDP sender/receiver demo.")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_server = sub.add_parser("server", help="Run as reliable UDP receiver")
    p_server.add_argument("--host", default="127.0.0.1")
    p_server.add_argument("--port", type=int, default=9000)
    p_server.add_argument("--idle-timeout", type=float, default=30.0)

    p_client = sub.add_parser("client", help="Run as reliable UDP sender")
    p_client.add_argument("--host", default="127.0.0.1")
    p_client.add_argument("--port", type=int, default=9000)
    p_client.add_argument("--messages", nargs="+", required=True)
    p_client.add_argument("--timeout", type=float, default=0.75)
    p_client.add_argument("--retries", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "server":
        receiver = ReliableUDPReceiver(args.host, args.port, args.idle_timeout)
        receiver.serve()
    else:
        sender = ReliableUDPSender(args.host, args.port, args.timeout, args.retries)
        start = time.time()
        sender.send_messages(args.messages)
        print(f"Done in {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
