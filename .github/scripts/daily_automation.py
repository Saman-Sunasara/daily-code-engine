"""
Daily repository automation runner.

Creates the next day folder with:
- data_structures.py
- networking.py
- game_features.py
- mini_tools.py

Then updates:
- task_history.json
- README.md
- DASHBOARD.md

It also writes `.daily_commit_message.txt` for CI commit step.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
HISTORY_FILE = ROOT / "task_history.json"
README_FILE = ROOT / "README.md"
DASHBOARD_FILE = ROOT / "DASHBOARD.md"
COMMIT_MSG_FILE = ROOT / ".daily_commit_message.txt"


def dsa_segment_tree_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Data Structures & Algorithms
Task: {title}
"""

from __future__ import annotations
import argparse


class SegmentTree:
    def __init__(self, data: list[int]) -> None:
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, data)

    def _build(self, node: int, left: int, right: int, data: list[int]) -> None:
        if left == right:
            self.tree[node] = data[left]
            return
        mid = (left + right) // 2
        self._build(node * 2, left, mid, data)
        self._build(node * 2 + 1, mid + 1, right, data)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def _push(self, node: int, left: int, right: int) -> None:
        if self.lazy[node] != 0:
            self.tree[node] += (right - left + 1) * self.lazy[node]
            if left != right:
                self.lazy[node * 2] += self.lazy[node]
                self.lazy[node * 2 + 1] += self.lazy[node]
            self.lazy[node] = 0

    def update_range(self, ql: int, qr: int, delta: int) -> None:
        self._update(1, 0, self.n - 1, ql, qr, delta)

    def _update(self, node: int, left: int, right: int, ql: int, qr: int, delta: int) -> None:
        self._push(node, left, right)
        if qr < left or right < ql:
            return
        if ql <= left and right <= qr:
            self.lazy[node] += delta
            self._push(node, left, right)
            return
        mid = (left + right) // 2
        self._update(node * 2, left, mid, ql, qr, delta)
        self._update(node * 2 + 1, mid + 1, right, ql, qr, delta)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def query_range(self, ql: int, qr: int) -> int:
        return self._query(1, 0, self.n - 1, ql, qr)

    def _query(self, node: int, left: int, right: int, ql: int, qr: int) -> int:
        self._push(node, left, right)
        if qr < left or right < ql:
            return 0
        if ql <= left and right <= qr:
            return self.tree[node]
        mid = (left + right) // 2
        return self._query(node * 2, left, mid, ql, qr) + self._query(node * 2 + 1, mid + 1, right, ql, qr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arr", nargs="*", type=int, default=[2, 1, 3, 4, 5, 2, 6])
    args = parser.parse_args()
    seg = SegmentTree(args.arr)
    print("Initial sum [1,5] =", seg.query_range(1, 5))
    seg.update_range(2, 4, 3)
    print("After +3 on [2,4], sum [1,5] =", seg.query_range(1, 5))


if __name__ == "__main__":
    main()
'''


def dsa_union_find_kruskal_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Data Structures & Algorithms
Task: {title}
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Edge:
    u: str
    v: str
    w: int


class DSU:
    def __init__(self, nodes: list[str]) -> None:
        self.parent = {{n: n for n in nodes}}
        self.rank = {{n: 0 for n in nodes}}

    def find(self, x: str) -> str:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: str, b: str) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal(nodes: list[str], edges: list[Edge]) -> tuple[int, list[Edge]]:
    dsu = DSU(nodes)
    total = 0
    mst: list[Edge] = []
    for e in sorted(edges, key=lambda x: x.w):
        if dsu.union(e.u, e.v):
            total += e.w
            mst.append(e)
    return total, mst


def main() -> None:
    nodes = ["A", "B", "C", "D", "E"]
    edges = [
        Edge("A", "B", 1), Edge("A", "C", 3), Edge("B", "C", 2),
        Edge("B", "D", 4), Edge("C", "D", 5), Edge("C", "E", 6), Edge("D", "E", 7)
    ]
    total, mst = kruskal(nodes, edges)
    print("MST total:", total)
    print("Edges:", [(e.u, e.v, e.w) for e in mst])


if __name__ == "__main__":
    main()
'''


def dsa_trie_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Data Structures & Algorithms
Task: {title}
"""

from __future__ import annotations
import argparse


class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {{}}
        self.end = False
        self.freq = 0


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.end = True
        node.freq += 1

    def suggest(self, prefix: str, limit: int = 5) -> list[tuple[str, int]]:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        out: list[tuple[str, int]] = []
        self._dfs(node, prefix, out)
        out.sort(key=lambda x: (-x[1], x[0]))
        return out[:limit]

    def _dfs(self, node: TrieNode, cur: str, out: list[tuple[str, int]]) -> None:
        if node.end:
            out.append((cur, node.freq))
        for ch, nxt in node.children.items():
            self._dfs(nxt, cur + ch, out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="net")
    args = parser.parse_args()
    trie = Trie()
    for word in ["network", "netcode", "netcat", "nested", "node", "network", "netcode", "next"]:
        trie.insert(word)
    print("Suggestions:", trie.suggest(args.prefix))


if __name__ == "__main__":
    main()
'''


def net_selective_repeat_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Networking
Task: {title}
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
    recv_buffer: dict[int, str] = {{}}
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
    msgs = [f"pkt-{{i}}" for i in range(12)]
    out = selective_repeat_sim(msgs, args.window, args.drop_rate)
    print("Delivered all:", out == msgs)
    print("Count:", len(out))


if __name__ == "__main__":
    main()
'''


def net_heartbeat_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Networking
Task: {title}
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
'''


def net_aimd_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Networking
Task: {title}
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
'''


def game_fsm_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Game Features
Task: {title}
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
            print(f"frame={{frame}} state={{enemy.state}} enemy_x={{enemy.x:.2f}} player_x={{player_x:.2f}}")


if __name__ == "__main__":
    main()
'''


def game_event_combat_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Game Features
Task: {title}
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
            print(f"tick={{tick}} player_hp={{player.hp}} enemy_hp={{enemy.hp}}")
        if player.hp <= 0 or enemy.hp <= 0:
            break


if __name__ == "__main__":
    main()
'''


def game_spatial_hash_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Game Features
Task: {title}
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
    grid: dict[tuple[int, int], list[int]] = {{}}
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
'''


def tool_incremental_backup_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Mini Tools
Task: {title}
"""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def run_backup(src: Path, dst: Path, state_file: Path) -> int:
    state = {{}}
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
    copied = 0
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        rel = str(f.relative_to(src))
        digest = file_hash(f)
        if state.get(rel) == digest:
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
        state[rel] = digest
        copied += 1
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return copied


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=".")
    parser.add_argument("--dst", default="_backup")
    parser.add_argument("--state", default=".backup/state.json")
    args = parser.parse_args()
    copied = run_backup(Path(args.src).resolve(), Path(args.dst).resolve(), Path(args.state).resolve())
    print("Copied files:", copied)


if __name__ == "__main__":
    main()
'''


def tool_log_analyzer_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Mini Tools
Task: {title}
"""

from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path


def summarize_log(path: Path) -> dict:
    counts = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        if "ERROR" in line:
            counts["ERROR"] += 1
        elif "WARN" in line:
            counts["WARN"] += 1
        elif "INFO" in line:
            counts["INFO"] += 1
        else:
            counts["OTHER"] += 1
    return dict(counts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    args = parser.parse_args()
    out = summarize_log(Path(args.log).resolve())
    print(out)


if __name__ == "__main__":
    main()
'''


def tool_release_notes_code(day: int, title: str) -> str:
    return f'''"""
Day {day} - Mini Tools
Task: {title}
"""

from __future__ import annotations
import argparse
import subprocess


def build_notes(limit: int) -> str:
    proc = subprocess.run(
        ["git", "log", f"-{{limit}}", "--pretty=format:%h %s"],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [f"- {{line}}" for line in proc.stdout.splitlines() if line.strip()]
    return "\\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    print("# Release Notes")
    print(build_notes(args.limit))


if __name__ == "__main__":
    main()
'''


TASKS = {
    "dsa": [
        {
            "title": "Segment tree with lazy propagation",
            "difficulty": "high",
            "generator": dsa_segment_tree_code,
        },
        {
            "title": "Union-Find + Kruskal minimum spanning tree",
            "difficulty": "high",
            "generator": dsa_union_find_kruskal_code,
        },
        {
            "title": "Trie-based autocomplete with frequency ranking",
            "difficulty": "high",
            "generator": dsa_trie_code,
        },
    ],
    "networking": [
        {
            "title": "Selective repeat reliability simulation with out-of-order buffering",
            "difficulty": "high",
            "generator": net_selective_repeat_code,
        },
        {
            "title": "UDP heartbeat monitor with liveness detection and retry logic",
            "difficulty": "high",
            "generator": net_heartbeat_code,
        },
        {
            "title": "AIMD congestion-control simulation with packet-loss response",
            "difficulty": "high",
            "generator": net_aimd_code,
        },
    ],
    "game": [
        {
            "title": "Enemy finite-state machine with patrol/chase/attack transitions",
            "difficulty": "high",
            "generator": game_fsm_code,
        },
        {
            "title": "Event-driven combat loop with cooldown system",
            "difficulty": "high",
            "generator": game_event_combat_code,
        },
        {
            "title": "Spatial-hash broad-phase collision detection",
            "difficulty": "high",
            "generator": game_spatial_hash_code,
        },
    ],
    "mini_tool": [
        {
            "title": "Incremental backup CLI using file-hash change detection",
            "difficulty": "high",
            "generator": tool_incremental_backup_code,
        },
        {
            "title": "Structured log analyzer CLI for level/error aggregation",
            "difficulty": "high",
            "generator": tool_log_analyzer_code,
        },
        {
            "title": "Release-notes generator CLI from git history",
            "difficulty": "high",
            "generator": tool_release_notes_code,
        },
    ],
}


FILE_MAP = {
    "dsa": "data_structures.py",
    "networking": "networking.py",
    "game": "game_features.py",
    "mini_tool": "mini_tools.py",
}


def normalize(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()


def norm_key(text: str) -> str:
    return " ".join(normalize(text))


def load_history() -> dict:
    if not HISTORY_FILE.exists():
        return {"project": "daily-project-engine", "total_days": 0, "days": []}
    return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))


def used_titles(history: dict) -> Dict[str, set[str]]:
    out = {k: set() for k in TASKS}
    for day in history.get("days", []):
        tasks = day.get("tasks", {})
        for cat in TASKS:
            if cat in tasks and "title" in tasks[cat]:
                out[cat].add(norm_key(tasks[cat]["title"]))
    return out


def choose_tasks(history: dict) -> Dict[str, dict]:
    used = used_titles(history)
    chosen: Dict[str, dict] = {}
    for cat, options in TASKS.items():
        pick = None
        for opt in options:
            if norm_key(opt["title"]) not in used[cat]:
                pick = opt
                break
        if pick is None:
            # Rotate with variant naming after exhausting pool.
            idx = history.get("total_days", 0) % len(options)
            base = options[idx]
            pick = dict(base)
            pick["title"] = f"{base['title']} (variant {history.get('total_days', 0) + 1})"
        chosen[cat] = pick
    return chosen


def write_day_files(day: int, tasks: Dict[str, dict]) -> None:
    day_dir = ROOT / "days" / f"day{day}"
    day_dir.mkdir(parents=True, exist_ok=True)
    for cat, info in tasks.items():
        content = info["generator"](day, info["title"])
        (day_dir / FILE_MAP[cat]).write_text(content, encoding="utf-8")


def update_history(history: dict, day: int, tasks: Dict[str, dict], date_str: str) -> dict:
    day_entry = {
        "day": day,
        "date": date_str,
        "tasks": {
            cat: {
                "title": tasks[cat]["title"],
                "difficulty": tasks[cat]["difficulty"],
                "file": f"days/day{day}/{FILE_MAP[cat]}",
            }
            for cat in ["dsa", "networking", "game", "mini_tool"]
        },
    }
    history["total_days"] = day
    history.setdefault("days", []).append(day_entry)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return history


def append_readme(day: int, tasks: Dict[str, dict]) -> None:
    if not README_FILE.exists():
        README_FILE.write_text("# Daily Project Engine\n\n", encoding="utf-8")
    current = README_FILE.read_text(encoding="utf-8")
    if f"## Day {day}" in current:
        return
    block = (
        f"\n## Day {day}\n"
        f"- DSA: {tasks['dsa']['title']}.\n"
        f"- Networking: {tasks['networking']['title']}.\n"
        f"- Game Feature: {tasks['game']['title']}.\n"
        f"- Mini Tool: {tasks['mini_tool']['title']}.\n"
    )
    README_FILE.write_text(current.rstrip() + "\n" + block, encoding="utf-8")


def rebuild_dashboard(history: dict) -> None:
    total = history.get("total_days", 0)
    dsa_count = net_count = game_count = tool_count = 0
    lines = [
        "# Dashboard",
        "",
        "## Summary",
        f"- Total days completed: {total}",
        "- Categories implemented:",
    ]
    for day in history.get("days", []):
        if "dsa" in day.get("tasks", {}):
            dsa_count += 1
        if "networking" in day.get("tasks", {}):
            net_count += 1
        if "game" in day.get("tasks", {}):
            game_count += 1
        if "mini_tool" in day.get("tasks", {}):
            tool_count += 1
    lines.extend(
        [
            f"  - DSA: {dsa_count}",
            f"  - Networking: {net_count}",
            f"  - Game Features: {game_count}",
            f"  - Mini Tools: {tool_count}",
            "",
            "## Difficulty Progression",
        ]
    )
    for day in history.get("days", []):
        d = day["day"]
        t = day["tasks"]
        lines.extend(
            [
                f"- Day {d}",
                f"  - DSA: {t['dsa']['difficulty'].title()} ({t['dsa']['title']})",
                f"  - Networking: {t['networking']['difficulty'].title()} ({t['networking']['title']})",
                f"  - Game: {t['game']['difficulty'].title()} ({t['game']['title']})",
                f"  - Tooling: {t['mini_tool']['difficulty'].title()} ({t['mini_tool']['title']})",
            ]
        )
    lines.extend(
        [
            "",
            "## Next-Day Guidance",
            "- Keep tasks non-repeating and increase complexity with practical constraints.",
            "- Prefer real-world reliability, simulation fidelity, and reusable tooling.",
        ]
    )
    DASHBOARD_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_commit_message(day: int, tasks: Dict[str, dict]) -> str:
    return (
        f"Day {day}: Implement {tasks['dsa']['title']} + "
        f"{tasks['networking']['title']} + "
        f"{tasks['game']['title']} + "
        f"{tasks['mini_tool']['title']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="")
    args = parser.parse_args()

    history = load_history()
    day = int(history.get("total_days", 0)) + 1
    chosen = choose_tasks(history)
    date_str = args.date.strip() or datetime.now(timezone.utc).date().isoformat()

    write_day_files(day, chosen)
    history = update_history(history, day, chosen, date_str)
    append_readme(day, chosen)
    rebuild_dashboard(history)

    msg = build_commit_message(day, chosen)
    COMMIT_MSG_FILE.write_text(msg + "\n", encoding="utf-8")
    print(msg)


if __name__ == "__main__":
    main()
