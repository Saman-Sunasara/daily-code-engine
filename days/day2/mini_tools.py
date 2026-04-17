"""
Day 2 - Mini Tools
Task: Daily workflow automation CLI for planning, validation, and commit message generation.

Examples:
  python mini_tools.py next-plan --history task_history.json
  python mini_tools.py validate-day --day 2
  python mini_tools.py build-commit --day 2 --history task_history.json
  python mini_tools.py auto-commit --day 2 --history task_history.json --dry-run
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Dict, List


TaskCatalog = Dict[str, List[Dict[str, str]]]


TASK_CATALOG: TaskCatalog = {
    "dsa": [
        {"title": "Dijkstra shortest path with path reconstruction", "difficulty": "medium"},
        {"title": "A* pathfinding on weighted grid with obstacle and terrain costs", "difficulty": "medium-high"},
        {"title": "Segment tree with lazy propagation", "difficulty": "high"},
    ],
    "networking": [
        {"title": "Reliable UDP stop-and-wait with sequence, ACK, checksum, retries", "difficulty": "medium"},
        {
            "title": "Reliable UDP Go-Back-N sliding window with cumulative ACK and FIN handshake",
            "difficulty": "medium-high",
        },
        {"title": "Selective repeat with out-of-order buffering", "difficulty": "high"},
    ],
    "game": [
        {"title": "2D player movement and tile collision resolution", "difficulty": "medium"},
        {"title": "Platform physics with jump, gravity, and projectile-enemy interaction", "difficulty": "medium-high"},
        {"title": "State machine driven AI and combat events", "difficulty": "high"},
    ],
    "mini_tool": [
        {"title": "CLI file organizer with dry-run and undo manifest", "difficulty": "medium"},
        {"title": "Daily workflow automation CLI for planning, validation, and auto-commit", "difficulty": "medium-high"},
        {"title": "Rule-driven automation with plugin hooks", "difficulty": "high"},
    ],
}


def load_history(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_title(text: str) -> str:
    compact = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return re.sub(r"\s+", " ", compact)


def collect_existing_titles(history: dict) -> Dict[str, set[str]]:
    existing = {k: set() for k in ["dsa", "networking", "game", "mini_tool"]}
    for day in history.get("days", []):
        tasks = day.get("tasks", {})
        for category, detail in tasks.items():
            title = detail.get("title")
            if title:
                existing[category].add(normalize_title(title))
    return existing


def propose_next_tasks(history: dict) -> Dict[str, Dict[str, str]]:
    existing = collect_existing_titles(history)
    proposal: Dict[str, Dict[str, str]] = {}
    for category, options in TASK_CATALOG.items():
        picked = None
        for candidate in options:
            if normalize_title(candidate["title"]) not in existing[category]:
                picked = candidate
                break
        if picked is None:
            # Catalog exhausted: repeat highest-difficulty category item with variant marker.
            last = options[-1]
            picked = {"title": f"{last['title']} (variant)", "difficulty": last["difficulty"]}
        proposal[category] = picked
    return proposal


def next_day_number(history: dict) -> int:
    return int(history.get("total_days", 0)) + 1


def build_commit_message(history: dict, day: int) -> str:
    day_entry = None
    for entry in history.get("days", []):
        if int(entry.get("day", -1)) == day:
            day_entry = entry
            break
    if not day_entry:
        raise ValueError(f"Day {day} not found in history.")

    tasks = day_entry["tasks"]
    return (
        f"Day {day}: Implement {tasks['dsa']['title']} + "
        f"{tasks['networking']['title']} + "
        f"{tasks['game']['title']} + "
        f"{tasks['mini_tool']['title']}"
    )


def validate_day(day: int) -> None:
    base = Path(f"days/day{day}")
    required = ["data_structures.py", "networking.py", "game_features.py", "mini_tools.py"]
    missing = [name for name in required if not (base / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing files: {missing}")

    targets = [str(base / name) for name in required]
    subprocess.run(["python", "-m", "py_compile", *targets], check=True)
    print(f"Validation passed for day {day}: {', '.join(required)}")


def run_auto_commit(day: int, history_path: Path, dry_run: bool) -> None:
    history = load_history(history_path)
    message = build_commit_message(history, day)
    add_targets = [f"days/day{day}", "README.md", "DASHBOARD.md", str(history_path)]

    if dry_run:
        print("Dry-run:")
        print("git add", " ".join(add_targets))
        print(f'git commit -m "{message}"')
        return

    subprocess.run(["git", "add", *add_targets], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    print("Commit created:", message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automation helper for long-running daily coding workflow.")
    sub = parser.add_subparsers(dest="command", required=True)

    next_plan = sub.add_parser("next-plan", help="Suggest the next day task set based on history")
    next_plan.add_argument("--history", default="task_history.json")

    validate = sub.add_parser("validate-day", help="Compile-check all required files for a day")
    validate.add_argument("--day", type=int, required=True)

    build = sub.add_parser("build-commit", help="Generate commit message for a given day from history")
    build.add_argument("--day", type=int, required=True)
    build.add_argument("--history", default="task_history.json")

    auto = sub.add_parser("auto-commit", help="Stage and commit a given day using generated message")
    auto.add_argument("--day", type=int, required=True)
    auto.add_argument("--history", default="task_history.json")
    auto.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "next-plan":
        history = load_history(Path(args.history))
        day = next_day_number(history)
        proposal = propose_next_tasks(history)
        print(f"Next day: {day}")
        for category in ["dsa", "networking", "game", "mini_tool"]:
            task = proposal[category]
            print(f"- {category}: {task['title']} [{task['difficulty']}]")
    elif args.command == "validate-day":
        validate_day(args.day)
    elif args.command == "build-commit":
        history = load_history(Path(args.history))
        print(build_commit_message(history, args.day))
    else:
        run_auto_commit(args.day, Path(args.history), args.dry_run)


if __name__ == "__main__":
    main()
