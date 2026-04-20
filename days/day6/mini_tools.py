"""
Day 6 - Mini Tools
Task: Release-notes generator CLI from git history (variant 6)
"""

from __future__ import annotations
import argparse
import subprocess


def build_notes(limit: int) -> str:
    proc = subprocess.run(
        ["git", "log", f"-{limit}", "--pretty=format:%h %s"],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [f"- {line}" for line in proc.stdout.splitlines() if line.strip()]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    print("# Release Notes")
    print(build_notes(args.limit))


if __name__ == "__main__":
    main()
