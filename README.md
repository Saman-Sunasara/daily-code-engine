# Daily Project Engine

A disciplined daily engineering repository that adds practical, runnable improvements each day across:
- data structures and algorithms
- networking systems
- game systems
- mini CLI tools

## Day 1
- DSA: Implemented weighted graph + Dijkstra shortest path with path reconstruction.
- Networking: Built reliable UDP stop-and-wait transport using sequence numbers, ACKs, checksum verification, and retry logic.
- Game Feature: Added player movement with acceleration/friction and robust tile-based collision resolution.
- Mini Tool: Added a CLI file organizer with category sorting, dry-run mode, manifest output, and undo workflow.

## Run Day 1 Modules
```bash
python days/day1/data_structures.py
python days/day1/game_features.py
python days/day1/networking.py server --port 9000
python days/day1/networking.py client --port 9000 --messages hello world
python days/day1/mini_tools.py run --base . --dry-run
```
