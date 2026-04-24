"""
Day 10 - Mini Tools
Task: Incremental backup CLI using file-hash change detection (variant 10)
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
    state = {}
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
