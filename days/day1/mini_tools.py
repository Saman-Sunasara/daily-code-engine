"""
Day 1 - Mini Tools
Task: CLI file organizer with manifest + undo support.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
from typing import Dict, Iterable, List


CATEGORY_MAP: Dict[str, str] = {
    ".py": "code",
    ".js": "code",
    ".ts": "code",
    ".json": "data",
    ".csv": "data",
    ".md": "docs",
    ".txt": "docs",
    ".jpg": "images",
    ".jpeg": "images",
    ".png": "images",
    ".gif": "images",
    ".zip": "archives",
    ".tar": "archives",
    ".gz": "archives",
}


def classify_file(path: Path) -> str:
    return CATEGORY_MAP.get(path.suffix.lower(), "others")


def iter_files(base: Path, recursive: bool) -> Iterable[Path]:
    iterator = base.rglob("*") if recursive else base.glob("*")
    for item in iterator:
        if item.is_file():
            yield item


def organize(base: Path, output_dir: Path, recursive: bool, dry_run: bool) -> List[dict]:
    manifest: List[dict] = []
    for file_path in iter_files(base, recursive):
        # Skip already organized files and manifest directory.
        if output_dir in file_path.parents:
            continue

        category = classify_file(file_path)
        target_dir = output_dir / category
        target_path = target_dir / file_path.name

        # Resolve collisions by appending an index.
        index = 1
        while target_path.exists():
            target_path = target_dir / f"{file_path.stem}_{index}{file_path.suffix}"
            index += 1

        manifest.append({"src": str(file_path), "dst": str(target_path), "category": category})
        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(target_path))

    return manifest


def save_manifest(manifest: List[dict], manifest_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def undo(manifest_path: Path, dry_run: bool) -> int:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored = 0
    for item in entries:
        src = Path(item["src"])
        dst = Path(item["dst"])
        if dst.exists():
            if not dry_run:
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(src))
            restored += 1
    return restored


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sort files by type and keep an undo manifest.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Organize files")
    p_run.add_argument("--base", default=".", help="Directory to scan")
    p_run.add_argument("--output", default="_organized", help="Output folder")
    p_run.add_argument("--recursive", action="store_true")
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument("--manifest", default="_organized/manifest.json")

    p_undo = sub.add_parser("undo", help="Undo using a manifest file")
    p_undo.add_argument("--manifest", default="_organized/manifest.json")
    p_undo.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "run":
        base = Path(args.base).resolve()
        output = Path(args.output).resolve()
        manifest = organize(base, output, args.recursive, args.dry_run)
        save_manifest(manifest, Path(args.manifest).resolve())
        print(f"Processed {len(manifest)} files")
        print(f"Manifest: {Path(args.manifest).resolve()}")
        if args.dry_run:
            print("Dry-run mode: no files were moved.")
    else:
        restored = undo(Path(args.manifest).resolve(), args.dry_run)
        print(f"Restored {restored} files")
        if args.dry_run:
            print("Dry-run mode: no files were moved.")


if __name__ == "__main__":
    main()
