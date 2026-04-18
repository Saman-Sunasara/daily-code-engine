"""
Day 4 - Mini Tools
Task: Structured log analyzer CLI for level/error aggregation
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
